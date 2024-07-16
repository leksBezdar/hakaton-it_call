from dataclasses import dataclass

from domain.exceptions.base import ApplicationException


@dataclass(eq=False)
class InvalidUsernameLength(ApplicationException):
    username_value: str

    @property
    def message(self) -> str:
        return f"Username length is invalid: {self.username_value}"


@dataclass(eq=False)
class EmptyUsername(ApplicationException):
    @property
    def message(self) -> str:
        return "Username is empty"


@dataclass(eq=False)
class EmptyEmail(ApplicationException):
    @property
    def message(self) -> str:
        return "User email is empty"


@dataclass(eq=False)
class InvalidEmailFormat(ApplicationException):
    email: str

    @property
    def message(self) -> str:
        return f"The provided email is invalid: {self.email}"


@dataclass(eq=False)
class InvalidUsernameCharacters(ApplicationException):
    value: str

    @property
    def message(self) -> str:
        return f"The provided username has invalid characters: {self.value}"


@dataclass(eq=False)
class UserAlreadyDeleted(ApplicationException):
    value: str

    @property
    def message(self) -> str:
        return f"User with id {self.value} has already been deleted"


@dataclass(eq=False)
class UserNotDeleted(ApplicationException):
    value: str

    @property
    def message(self) -> str:
        return f"User with id {self.value} has not been deleted"


@dataclass(eq=False)
class UserAlreadySubscribed(ApplicationException):
    value: str

    @property
    def message(self) -> str:
        return f"User with id {self.value} is already subscribed to email notifications"


@dataclass(eq=False)
class UserIsNotSubscribed(ApplicationException):
    value: str

    @property
    def message(self) -> str:
        return f"User with id {self.value} is not subscribed to email notifications"


@dataclass(eq=False)
class EmptyTimezone(ApplicationException):
    @property
    def message(self) -> str:
        return "User timezone is empty"


@dataclass(eq=False)
class InvalidTimezone(ApplicationException):
    value: str

    @property
    def message(self) -> str:
        return f"The provided timezone is invalid: {self.value}"
