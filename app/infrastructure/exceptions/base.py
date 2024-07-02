from dataclasses import dataclass

from domain.exceptions.base import ApplicationException


@dataclass(eq=False)
class InfrastructureException(ApplicationException):
    @property
    def message(self) -> str:
        return "Infractructure exeption has occurred"


@dataclass(eq=False)
class RepositoryException(InfrastructureException):
    @property
    def message(self) -> str:
        return "Repository exeption has occurred"
