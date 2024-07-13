from dataclasses import dataclass
import smtplib

from infrastructure.exceptions.senders import SMTPAuthenticationException
from infrastructure.services.smtp.base import ISMTPClient


@dataclass
class GmailSMTPClient(ISMTPClient):
    def login(self, server: smtplib.SMTP) -> None:
        try:
            server.login(self.sender_mail, self.smtp_app_password)
        except smtplib.SMTPAuthenticationError:
            raise SMTPAuthenticationException
        except smtplib.SMTPException:
            raise smtplib.SMTPException
