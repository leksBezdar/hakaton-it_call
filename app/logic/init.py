from functools import lru_cache
from uuid import uuid4
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from punq import Container, Scope
import redis  # type: ignore


from domain.events.users import UserSubscribedEvent, UserUnsubscribedEvent
from infrastructure.message_brokers.base import IMessageBroker
from infrastructure.message_brokers.kafka import KafkaMessageBroker
from infrastructure.repositories.users.base import IUserRepository
from infrastructure.repositories.users.sqlalchemy import SqlAlchemyUserRepository
from infrastructure.services.smtp.scheduler.base import IScheduler
from infrastructure.services.smtp.scheduler.scheduler import EmailScheduler
from infrastructure.services.otps.base import IOTPService
from infrastructure.services.otps.redis import RedisOTPService
from infrastructure.services.smtp.senders.base import ISenderService
from infrastructure.services.smtp.senders.composed import ComposedSenderService
from infrastructure.services.smtp.senders.dummy import DummySenderService
from infrastructure.services.smtp.senders.smtp import EmailSenderService
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
from logic.events.users import UserSubscribedEventHandler, UserUnsubscribedEventHandler
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

    settings: Settings = container.resolve(Settings)

    def init_user_sqlalchemy_repository() -> IUserRepository:
        return SqlAlchemyUserRepository()

    def init_redis_otp_service() -> IOTPService:
        return RedisOTPService(
            redis_client=redis.Redis(
                host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
            )
        )

    def init_smtplib_sender_service() -> ISenderService:
        return EmailSenderService(
            sender_mail=settings.SENDER_MAIL,
            smtp_app_password=settings.SMTP_APP_PASSWORD,
            smtp_url=settings.SMTP_URL,
            confirm_url=settings.CONFIRM_URL,
        )

    def init_email_scheduler() -> EmailScheduler:
        return EmailScheduler(
            settings=settings,
            message_broker=container.resolve(IMessageBroker),
            sender_mail=settings.SENDER_MAIL,
            smtp_app_password=settings.SMTP_APP_PASSWORD,
            smtp_url=settings.SMTP_URL,
            main_page_url=settings.MAIN_PAGE_URL,
            user_repository=container.resolve(IUserRepository),
        )

    # Services
    container.register(
        IOTPService, factory=init_redis_otp_service, scope=Scope.singleton
    )
    container.register(
        ISenderService,
        ComposedSenderService,
        sender_services=(
            DummySenderService(),
            init_smtplib_sender_service(),
        ),
    )
    container.register(IScheduler, factory=init_email_scheduler, scope=Scope.singleton)

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
            otp_service=container.resolve(IOTPService),
            sender_service=container.resolve(ISenderService),
        )
        user_confirm_login_handler = UserConfirmLoginCommandHandler(
            _mediator=mediator,
            user_repository=container.resolve(IUserRepository),
            otp_service=container.resolve(IOTPService),
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

        # Event Handlers
        user_subscribed_event_handler = UserSubscribedEventHandler(
            broker_topic=settings.user_subscribed_event_topic,
            message_broker=container.resolve(IMessageBroker),
        )
        user_unsubscribed_event_handler = UserUnsubscribedEventHandler(
            broker_topic=settings.user_unsubscribed_event_topic,
            message_broker=container.resolve(IMessageBroker),
        )
        mediator.register_event(
            UserSubscribedEvent,
            [user_subscribed_event_handler],
        )
        mediator.register_event(
            UserUnsubscribedEvent,
            [user_unsubscribed_event_handler],
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
