from dataclasses import dataclass

from domain.exceptions.base import ApplicationException


@dataclass(eq=False)
class CodeWasNotFoundException(ApplicationException):
    code: str

    @property
    def message(self) -> str:
        return f"The provided code was not found: {self.code}"


@dataclass(eq=False)
class CodesAreNotEqualException(ApplicationException):
    code: str
    cached_code: str
    user_email: str

    @property
    def message(self) -> str:
        return (
            f"The provided code does not match the cached code for user with email {self.user_email}: "
            f"provided code: {self.code}, cached code: {self.cached_code}"
        )
