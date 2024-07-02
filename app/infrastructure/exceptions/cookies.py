from dataclasses import dataclass

from infrastructure.exceptions.base import InfrastructureException


@dataclass(eq=False)
class InvalidToken(InfrastructureException):
    @property
    def message(self) -> str:
        return "Token is invalid"


@dataclass(eq=False)
class ExpiredToken(InfrastructureException):
    @property
    def message(self) -> str:
        return "Token has expired"
