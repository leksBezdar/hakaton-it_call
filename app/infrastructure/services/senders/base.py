from abc import ABC, abstractmethod

from domain.entities.users import UserEntity


class ISenderService(ABC):
    @abstractmethod
    def send_code(self, user: UserEntity, code: str) -> None: ...
