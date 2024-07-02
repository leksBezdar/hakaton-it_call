from functools import lru_cache
from uuid import uuid4
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from punq import Container, Scope


from infrastructure.message_brokers.base import IMessageBroker
from infrastructure.message_brokers.kafka import KafkaMessageBroker
from infrastructure.repositories.users.base import IUserRepository
from infrastructure.repositories.users.sqlalchemy import SqlAlchemyUserRepository
from infrastructure.security.cookies.base import ICookieManager
from infrastructure.security.cookies.jwt import PyJWTCookieManager
from logic.commands.users import (
    ChangePasswordCommand,
    ChangePasswordCommandHandler,
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
    UserLoginCommand,
    UserLoginCommandHandler,
)
from logic.mediator.base import Mediator
from logic.mediator.event import EventMediator

from logic.queries.users import (
    GetTokensQuery,
    GetTokensQueryHandler,
    GetUserByIdQuery,
    GetUserByIdQueryHandler,
    GetUserByUsernameQuery,
    GetUserByUsernameQueryHandler,
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

    def init_cookie_manager() -> ICookieManager:
        return PyJWTCookieManager(
            _token_secret_key=settings.token_secret_key,
            _algorithm=settings.algorithm,
            _access_token_expire_minutes=settings.access_token_expire_minutes,
            _refresh_token_expire_days=settings.refresh_token_expire_days,
        )

    # Repositories
    container.register(
        IUserRepository, factory=init_user_sqlalchemy_repository, scope=Scope.singleton
    )
    container.register(
        ICookieManager, factory=init_cookie_manager, scope=Scope.singleton
    )

    # Command handlers
    container.register(CreateUserCommandHandler)
    container.register(UserLoginCommandHandler)
    container.register(ChangeUsernameCommandHandler)
    container.register(ChangePasswordCommandHandler)
    container.register(SubscribeToEmailSenderCommandHandler)
    container.register(UnsubscribeFromEmailSenderCommandHandler)
    container.register(RestoreUserCommandHandler)
    container.register(DeleteUserCommandHandler)

    # Query Handlers
    container.register(GetTokensQueryHandler)
    container.register(GetUsersQueryHandler)
    container.register(GetUserByIdQueryHandler)
    container.register(GetUserByUsernameQueryHandler)

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
        )
        change_username_handler = ChangeUsernameCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
        )
        change_password_handler = ChangePasswordCommandHandler(
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
            ChangeUsernameCommand,
            [change_username_handler],
        )
        mediator.register_command(
            ChangePasswordCommand,
            [change_password_handler],
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
            GetTokensQuery,
            container.resolve(GetTokensQueryHandler),
        )
        mediator.register_query(
            GetUsersQuery,
            container.resolve(GetUsersQueryHandler),
        )
        mediator.register_query(
            GetUserByIdQuery,
            container.resolve(GetUserByIdQueryHandler),
        )
        mediator.register_query(
            GetUserByUsernameQuery,
            container.resolve(GetUserByUsernameQueryHandler),
        )

        return mediator

    container.register(Mediator, factory=init_mediator)
    container.register(EventMediator, factory=init_mediator)

    return container
