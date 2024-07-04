from dataclasses import dataclass
from typing import Iterable

from domain.entities.users import UserEntity
from infrastructure.services.senders.base import ISenderService


@dataclass
class ComposedSenderService(ISenderService):
    sender_services: Iterable[ISenderService]

    def send_otp(self, user: UserEntity, otp: str) -> None:
        for service in self.sender_services:
            service.send_otp(user=user, otp=otp)
