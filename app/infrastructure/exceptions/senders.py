from dataclasses import dataclass

from infrastructure.exceptions.base import ServiceException


@dataclass(eq=False)
class SMTPAuthenticationException(ServiceException):
    @property
    def message(self) -> str:
        return "The provided credentials are incorrect"


@dataclass(eq=False)
class SMTPException(ServiceException):
    error: Exception

    @property
    def message(self) -> str:
        return f"An unexcepted smtp error: {self.error}"


@dataclass(eq=False)
class SMTPRecipientsRefused(ServiceException):
    @property
    def message(self) -> str:
        return "The recipient was refused by the server"


@dataclass(eq=False)
class SMTPSenderRefused(ServiceException):
    @property
    def message(self) -> str:
        return "The sender address was refused by the server"


@dataclass(eq=False)
class SMTPDataError(ServiceException):
    @property
    def message(self) -> str:
        return "The SMTP server refused the message data"
