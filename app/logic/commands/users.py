from dataclasses import dataclass

from domain.entities.users import UserEntity
from domain.values.users import UserEmail, Username
from infrastructure.repositories.users.base import (
    IUserRepository,
)
from infrastructure.services.codes.base import ICodeService
from infrastructure.services.senders.base import ISenderService
from logic.commands.base import BaseCommand, CommandHandler
from logic.exceptions.users import (
    UserAlreadyExistsException,
    UserNotFoundException,
    UsernameAlreadyExistsException,
)


@dataclass(frozen=True)
class CreateUserCommand(BaseCommand):
    username: str
    email: str
    is_subscribed: bool


@dataclass(frozen=True)
class CreateUserCommandHandler(CommandHandler[CreateUserCommand, UserEntity]):
    user_repository: IUserRepository

    async def handle(self, command: CreateUserCommand) -> UserEntity:
        username = Username(value=command.username)
        email = UserEmail(value=command.email)

        # TODO move existing check to entity layer
        if await self.user_repository.check_user_exists_by_email_and_username(
            email=email.as_generic_type(), username=username.as_generic_type()
        ):
            raise UserAlreadyExistsException()

        new_user = await UserEntity.create(
            username=username,
            email=email,
            is_subscribed=command.is_subscribed,
        )

        await self.user_repository.add(new_user)
        await self._mediator.publish(new_user.pull_events())

        return new_user


@dataclass(frozen=True)
class UserLoginCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class UserLoginCommandHandler(CommandHandler[UserLoginCommand, None]):
    user_repository: IUserRepository
    code_service: ICodeService
    sender_service: ISenderService

    async def handle(self, command: UserLoginCommand) -> None:
        user = await self.user_repository.get_by_email(email=command.email)

        if not user:
            raise UserNotFoundException(value=command.email)

        code = self.code_service.generate_code(user=user)
        self.sender_service.send_code(user=user, code=code)


@dataclass(frozen=True)
class UserConfirmLoginCommand(BaseCommand):
    email: str
    verification_token: str


@dataclass(frozen=True)
class UserConfirmLoginCommandHandler(
    CommandHandler[UserConfirmLoginCommand, UserEntity]
):
    user_repository: IUserRepository
    code_service: ICodeService

    async def handle(self, command: UserConfirmLoginCommand) -> UserEntity:
        user = await self.user_repository.get_by_email(email=command.email)

        if not user:
            raise UserNotFoundException(value=command.email)

        self.code_service.validate(code=command.verification_token, user=user)
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
