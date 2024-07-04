from dataclasses import dataclass

from domain.entities.users import UserEntity
from infrastructure.services.senders.base import ISenderService


@dataclass
class EmailSenderService(ISenderService):
    # TODO: replace with aiosmtplib implementation
    def send_otp(self, user: UserEntity, otp: str) -> None:
        print(f"OTP {otp} was sent to user: {user} via email")
