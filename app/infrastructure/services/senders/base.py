from abc import ABC, abstractmethod

from domain.entities.users import UserEntity


class ISenderService(ABC):
    @abstractmethod
    def send_otp(self, user: UserEntity, otp: str) -> None: ...
