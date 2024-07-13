from abc import ABC, abstractmethod
from dataclasses import dataclass
import smtplib


@dataclass
class ISMTPClient(ABC):
    sender_mail: str
    smtp_app_password: str
    smtp_url: tuple[str, int]

    @abstractmethod
    def login(self, server: smtplib.SMTP) -> None: ...
