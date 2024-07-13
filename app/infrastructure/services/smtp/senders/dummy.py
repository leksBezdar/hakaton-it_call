from dataclasses import dataclass

from domain.entities.users import UserEntity
from infrastructure.services.smtp.senders.base import ISenderService


@dataclass
class DummySenderService(ISenderService):
    def send_otp(self, user: UserEntity, otp: str) -> None:
        print(f"OTP {otp} was sent to user: {user}")
