from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from domain.entities.users import UserEntity
from infrastructure.exceptions.senders import (
    SMTPAuthenticationException,
    SMTPDataError,
    SMTPException,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
)
from infrastructure.services.senders.base import ISenderService
from infrastructure.services.senders.mails.otps import OTPMessage


@dataclass
class EmailSenderService(ISenderService):
    sender_mail: str
    smtp_app_password: str
    smtp_url: tuple[str, int]
    confirm_url: str

    def login(self, server: smtplib.SMTP) -> None:
        try:
            server.login(self.sender_mail, self.smtp_app_password)
        except smtplib.SMTPAuthenticationError:
            raise SMTPAuthenticationException
        except smtplib.SMTPException:
            raise SMTPException

    def build_message(self, user: UserEntity, otp: str) -> MIMEMultipart:
        otp_message = OTPMessage(user=user, otp=otp, confirm_url=self.confirm_url)

        msg = MIMEMultipart("alternative")
        msg["From"] = self.sender_mail
        msg["To"] = user.email.as_generic_type()
        msg["Subject"] = otp_message.subject

        msg.attach(MIMEText(otp_message.body, "html"))

        return msg

    def send_otp(self, user: UserEntity, otp: str) -> None:
        with smtplib.SMTP(*self.smtp_url) as server:
            server.starttls()
            self.login(server)

            msg = self.build_message(user, otp)

            try:
                server.sendmail(
                    from_addr=self.sender_mail,
                    to_addrs=user.email.as_generic_type(),
                    msg=msg.as_string(),
                )
            except smtplib.SMTPRecipientsRefused:
                raise SMTPRecipientsRefused
            except smtplib.SMTPSenderRefused:
                raise SMTPSenderRefused
            except smtplib.SMTPDataError:
                raise SMTPDataError
