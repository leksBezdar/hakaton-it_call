from dataclasses import dataclass

from domain.entities.users import UserEntity
from infrastructure.exceptions.senders import (
    SMTPAuthenticationException,
    SMTPDataError,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
)
from infrastructure.services.senders.base import ISenderService
import smtplib


# TODO: replace with aiosmtplib implementation
@dataclass
class EmailSenderService(ISenderService):
    sender_mail: str
    smtp_app_password: str
    server: smtplib.SMTP

    def login(self) -> None:
        try:
            self.server.login(self.sender_mail, self.smtp_app_password)
        except smtplib.SMTPAuthenticationError:
            raise SMTPAuthenticationException
        except smtplib.SMTPException:
            raise smtplib.SMTPException

    def send_otp(self, user: UserEntity, otp: str) -> None:
        self.server.starttls()
        self.login()

        try:
            self.server.sendmail(
                from_addr=self.sender_mail,
                to_addrs=user.email.as_generic_type(),
                msg=otp,
            )

        except smtplib.SMTPRecipientsRefused:
            raise SMTPRecipientsRefused
        except smtplib.SMTPSenderRefused:
            raise SMTPSenderRefused
        except smtplib.SMTPDataError:
            raise SMTPDataError
        finally:
            self.server.quit()
