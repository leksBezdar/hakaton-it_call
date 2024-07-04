from dataclasses import dataclass

from domain.exceptions.base import ApplicationException


@dataclass(eq=False)
class OTPWasNotFoundException(ApplicationException):
    otp: str

    @property
    def message(self) -> str:
        return f"The provided one-time password was not found: {self.otp}"


@dataclass(eq=False)
class OTPsAreNotEqualException(ApplicationException):
    otp: str
    cached_otp: str
    user_email: str

    @property
    def message(self) -> str:
        return f"The provided one-time password does not match the cached one for user with email {self.user_email}"
