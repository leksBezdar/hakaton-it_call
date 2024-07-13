from dataclasses import dataclass

from domain.entities.users import UserEntity
from domain.values.users import UserEmail, UserTimezone, Username
from infrastructure.repositories.users.base import (
    IUserRepository,
)
from infrastructure.services.otps.base import IOTPService
from infrastructure.services.smtp.senders.base import ISenderService
from logic.commands.base import BaseCommand, CommandHandler
from logic.exceptions.users import (
    IncorrectEmailAddress,
    UserAlreadyExistsException,
    UserNotFoundException,
    UsernameAlreadyExistsException,
)
from validate_email import validate_email


@dataclass(frozen=True)
class CreateUserCommand(BaseCommand):
    username: str
    email: str
    user_timezone: str
    is_subscribed: bool


@dataclass(frozen=True)
class CreateUserCommandHandler(CommandHandler[CreateUserCommand, UserEntity]):
    user_repository: IUserRepository

    async def handle(self, command: CreateUserCommand) -> UserEntity:
        if not self.check_if_email_valid(email=command.email):
            raise IncorrectEmailAddress(command.email)

        username = Username(value=command.username)
        email = UserEmail(value=command.email)
        user_timezone = UserTimezone(value=command.user_timezone)

        # TODO move existing check to entity layer
        if await self.user_repository.check_user_exists_by_email_and_username(
            email=email.as_generic_type(), username=username.as_generic_type()
        ):
            raise UserAlreadyExistsException()

        new_user = await UserEntity.create(
            username=username,
            email=email,
            user_timezone=user_timezone,
            is_subscribed=command.is_subscribed,
        )

        await self.user_repository.add(new_user)
        await self._mediator.publish(new_user.pull_events())

        return new_user

    def check_if_email_valid(self, email: str) -> bool:
        return validate_email(email_address=email)


@dataclass(frozen=True)
class UserLoginCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class UserLoginCommandHandler(CommandHandler[UserLoginCommand, None]):
    user_repository: IUserRepository
    otp_service: IOTPService
    sender_service: ISenderService

    async def handle(self, command: UserLoginCommand) -> None:
        user = await self.user_repository.get_by_email(email=command.email)

        if not user:
            raise UserNotFoundException(value=command.email)

        otp = self.otp_service.generate_otp(user=user)
        self.sender_service.send_otp(user=user, otp=otp)


@dataclass(frozen=True)
class UserConfirmLoginCommand(BaseCommand):
    email: str
    otp: str


@dataclass(frozen=True)
class UserConfirmLoginCommandHandler(
    CommandHandler[UserConfirmLoginCommand, UserEntity]
):
    user_repository: IUserRepository
    otp_service: IOTPService

    async def handle(self, command: UserConfirmLoginCommand) -> UserEntity:
        user = await self.user_repository.get_by_email(email=command.email)

        if not user:
            raise UserNotFoundException(value=command.email)

        self.otp_service.validate(otp=command.otp, user=user)
        await user.confirm_login()
        await self._mediator.publish(user.pull_events())

        return user


@dataclass(frozen=True)
class ChangeUsernameCommand(BaseCommand):
    user_oid: str
    new_username: str


@dataclass(frozen=True)
class ChangeUsernameCommandHandler(CommandHandler[ChangeUsernameCommand, None]):
    user_repository: IUserRepository

    async def handle(self, command: ChangeUsernameCommand) -> None:
        user = await self.user_repository.get_by_oid(oid=command.user_oid)
        if not user:
            raise UserNotFoundException(value=command.user_oid)

        if command.new_username != user.username.as_generic_type():
            existing_usernames = await self.user_repository.get_existing_usernames()

            if command.new_username in existing_usernames:
                raise UsernameAlreadyExistsException(command.new_username)

            new_username = Username(value=command.new_username)
            await user.change_username(new_username=new_username)
            await self.user_repository.update(user)
            await self._mediator.publish(user.pull_events())


@dataclass(frozen=True)
class SubscribeToEmailSenderCommand(BaseCommand):
    user_oid: str


@dataclass(frozen=True)
class SubscribeToEmailSenderCommandHandler(
    CommandHandler[SubscribeToEmailSenderCommand, None]
):
    user_repository: IUserRepository

    async def handle(self, command: SubscribeToEmailSenderCommand):
        user = await self.user_repository.get_by_oid(oid=command.user_oid)
        if not user:
            raise UserNotFoundException(value=command.user_oid)

        await user.subscribe_to_email_sender()
        await self.user_repository.update(user)
        await self._mediator.publish(user.pull_events())


@dataclass(frozen=True)
class UnsubscribeFromEmailSenderCommand(BaseCommand):
    user_oid: str


@dataclass(frozen=True)
class UnsubscribeFromEmailSenderCommandHandler(
    CommandHandler[UnsubscribeFromEmailSenderCommand, None]
):
    user_repository: IUserRepository

    async def handle(self, command: UnsubscribeFromEmailSenderCommand) -> None:
        user = await self.user_repository.get_by_oid(oid=command.user_oid)
        if not user:
            raise UserNotFoundException(value=command.user_oid)

        await user.unsubscribe_from_email_sender()
        await self.user_repository.update(user)
        await self._mediator.publish(user.pull_events())


@dataclass(frozen=True)
class RestoreUserCommand(BaseCommand):
    user_oid: str


@dataclass(frozen=True)
class RestoreUserCommandHandler(CommandHandler[RestoreUserCommand, None]):
    user_repository: IUserRepository

    async def handle(self, command: RestoreUserCommand) -> None:
        user = await self.user_repository.get_by_oid(oid=command.user_oid)
        if not user:
            raise UserNotFoundException(value=command.user_oid)

        await user.restore()
        await self.user_repository.restore(user)
        await self._mediator.publish(user.pull_events())


@dataclass(frozen=True)
class DeleteUserCommand(BaseCommand):
    user_oid: str


@dataclass(frozen=True)
class DeleteUserCommandHandler(CommandHandler[DeleteUserCommand, None]):
    user_repository: IUserRepository

    async def handle(self, command: DeleteUserCommand) -> None:
        user = await self.user_repository.get_by_oid(oid=command.user_oid)

        if not user:
            raise UserNotFoundException(value=command.user_oid)

        await user.delete()
        await self.user_repository.delete(oid=command.user_oid)
        await self._mediator.publish(user.pull_events())
