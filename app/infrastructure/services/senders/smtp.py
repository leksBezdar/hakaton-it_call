from dataclasses import dataclass

from domain.entities.users import UserEntity
from infrastructure.services.senders.base import ISenderService


@dataclass
class EmailSenderService(ISenderService):
    # TODO: replace with aiosmtplib implementation
    def send_code(self, user: UserEntity, code: str) -> None:
        print(f"Code {code} was sent to user: {user} via email")
