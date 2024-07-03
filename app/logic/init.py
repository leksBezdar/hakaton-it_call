from functools import lru_cache
from uuid import uuid4
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from punq import Container, Scope
import redis


from infrastructure.message_brokers.base import IMessageBroker
from infrastructure.message_brokers.kafka import KafkaMessageBroker
from infrastructure.repositories.users.base import IUserRepository
from infrastructure.repositories.users.sqlalchemy import SqlAlchemyUserRepository
from infrastructure.services.codes.base import ICodeService
from infrastructure.services.codes.redis import RedisCodeService
from infrastructure.services.senders.base import ISenderService
from infrastructure.services.senders.composed import ComposedSenderService
from infrastructure.services.senders.dummy import DummySenderService
from infrastructure.services.senders.smtp import EmailSenderService
from logic.commands.users import (
    ChangeUsernameCommand,
    ChangeUsernameCommandHandler,
    CreateUserCommand,
    CreateUserCommandHandler,
    DeleteUserCommand,
    DeleteUserCommandHandler,
    RestoreUserCommand,
    RestoreUserCommandHandler,
    SubscribeToEmailSenderCommand,
    SubscribeToEmailSenderCommandHandler,
    UnsubscribeFromEmailSenderCommand,
    UnsubscribeFromEmailSenderCommandHandler,
    UserConfirmLoginCommand,
    UserConfirmLoginCommandHandler,
    UserLoginCommand,
    UserLoginCommandHandler,
)
from logic.mediator.base import Mediator
from logic.mediator.event import EventMediator

from logic.queries.users import (
    GetUserByIdQuery,
    GetUserByIdQueryHandler,
    GetUsersQuery,
    GetUsersQueryHandler,
)
from settings.settings import Settings


@lru_cache(1)
def init_container() -> Container:
    return _init_container()


def _init_container() -> Container:
    container = Container()

    container.register(Settings, instance=Settings(), scope=Scope.singleton)
    settings: Settings = container.resolve(Settings)  # noqa

    def init_user_sqlalchemy_repository() -> IUserRepository:
        return SqlAlchemyUserRepository()

    def init_redis_code_service() -> ICodeService:
        return RedisCodeService(
            redis_client=redis.Redis(
                host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
            )
        )

    # Services
    container.register(
        ICodeService, factory=init_redis_code_service, scope=Scope.singleton
    )
    container.register(
        ISenderService,
        ComposedSenderService,
        sender_services=(
            DummySenderService(),
            EmailSenderService(),
        ),
    )

    # Repositories
    container.register(
        IUserRepository, factory=init_user_sqlalchemy_repository, scope=Scope.singleton
    )
    # Command handlers
    container.register(CreateUserCommandHandler)
    container.register(UserLoginCommandHandler)
    container.register(UserConfirmLoginCommandHandler)
    container.register(ChangeUsernameCommandHandler)
    container.register(SubscribeToEmailSenderCommandHandler)
    container.register(UnsubscribeFromEmailSenderCommandHandler)
    container.register(RestoreUserCommandHandler)
    container.register(DeleteUserCommandHandler)

    # Query Handlers
    container.register(GetUsersQueryHandler)
    container.register(GetUserByIdQueryHandler)

    # Message broker
    def create_message_broker() -> IMessageBroker:
        return KafkaMessageBroker(
            producer=AIOKafkaProducer(bootstrap_servers=settings.KAFKA_URL),
            consumer=AIOKafkaConsumer(
                bootstrap_servers=settings.KAFKA_URL,
                group_id=f"{uuid4()}",
                metadata_max_age_ms=30000,
            ),
        )

    container.register(
        IMessageBroker, factory=create_message_broker, scope=Scope.singleton
    )

    # Mediator
    def init_mediator() -> Mediator:
        mediator = Mediator()

        # Command Handlers
        create_user_handler = CreateUserCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
        )
        user_login_handler = UserLoginCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
            code_service=container.resolve(ICodeService),
            sender_service=container.resolve(ISenderService),
        )
        user_confirm_login_handler = UserConfirmLoginCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
            code_service=container.resolve(ICodeService),
        )
        change_username_handler = ChangeUsernameCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
        )
        subscribe_to_email_sender_handler = SubscribeToEmailSenderCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
        )
        unsubscribe_from_email_sender_handler = (
            UnsubscribeFromEmailSenderCommandHandler(
                _mediator=mediator,
                user_repository=container.resolve(IUserRepository),
            )
        )
        restore_user_handler = RestoreUserCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
        )
        delete_user_handler = DeleteUserCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
        )
        mediator.register_command(
            CreateUserCommand,
            [create_user_handler],
        )
        mediator.register_command(
            UserLoginCommand,
            [user_login_handler],
        )
        mediator.register_command(
            UserConfirmLoginCommand,
            [user_confirm_login_handler],
        )
        mediator.register_command(
            ChangeUsernameCommand,
            [change_username_handler],
        )
        mediator.register_command(
            SubscribeToEmailSenderCommand,
            [subscribe_to_email_sender_handler],
        )
        mediator.register_command(
            UnsubscribeFromEmailSenderCommand,
            [unsubscribe_from_email_sender_handler],
        )
        mediator.register_command(
            RestoreUserCommand,
            [restore_user_handler],
        )
        mediator.register_command(
            DeleteUserCommand,
            [delete_user_handler],
        )

        # Query Handlers
        mediator.register_query(
            GetUsersQuery,
            container.resolve(GetUsersQueryHandler),
        )
        mediator.register_query(
            GetUserByIdQuery,
            container.resolve(GetUserByIdQueryHandler),
        )

        return mediator

    container.register(Mediator, factory=init_mediator)
    container.register(EventMediator, factory=init_mediator)

    return container
