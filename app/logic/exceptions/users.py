from dataclasses import dataclass

from logic.exceptions.base import LogicException


@dataclass(eq=False)
class UserAlreadyExistsException(LogicException):
    @property
    def message(self) -> str:
        return "User already exists"


@dataclass(eq=False)
class UserNotFoundException(LogicException):
    value: str

    @property
    def message(self) -> str:
        return f"User with {self.value=} was not found"


@dataclass(eq=False)
class InvalidCredentialsException(LogicException):
    @property
    def message(self) -> str:
        return "Invalid credentials were provided"


@dataclass(eq=False)
class UsernameAlreadyExistsException(LogicException):
    value: str

    @property
    def message(self) -> str:
        return f"User with username {self.value} already exists"


@dataclass(eq=False)
class IncorrectEmailAddress(LogicException):
    value: str

    @property
    def message(self) -> str:
        return f"This email address does not exist {self.value}"
