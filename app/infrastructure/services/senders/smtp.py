from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from dataclasses import dataclass
from domain.entities.users import UserEntity
from infrastructure.exceptions.senders import (
    SMTPAuthenticationException,
    SMTPDataError,
    SMTPException,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
)
from infrastructure.services.senders.base import ISenderService


@dataclass
class EmailSenderService(ISenderService):
    sender_mail: str
    smtp_app_password: str
    server: smtplib.SMTP
    confirm_url: str

    def login(self) -> None:
        try:
            self.server.login(self.sender_mail, self.smtp_app_password)
        except smtplib.SMTPAuthenticationError:
            raise SMTPAuthenticationException
        except smtplib.SMTPException:
            raise SMTPException

    def build_message_body(self, user: UserEntity, otp: str, subject: str) -> str:
        body = f"""
            <html>
                <head>
                    <style>
                        body {{
                        font-family: Arial, sans-serif;
                        font-size: 16px;
                        line-height: 1.6;
                        color: #333;
                        }}
                        .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        background-color: #f9f9f9;
                        }}
                        .header {{
                        background-color: #007bff;
                        color: #fff;
                        padding: 20px 10px;
                        text-align: center;
                        border-radius: 8px 8px 0 0;
                        }}
                        .content {{
                        padding: 20px;
                        text-align: center;
                        }}
                        .footer {{
                        background-color: #f0f0f0;
                        padding: 10px;
                        text-align: center;
                        border-radius: 0 0 8px 8px;
                        }}
                        .button {{
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #007bff;
                        color: #fff;
                        text-decoration: none;
                        border-radius: 5px;
                        }}
                        .button:hover {{
                        background-color: #0056b3;
                        }}
                    </style>
                </head>
                <body>
                        <div class="container">
                        <div class="header">
                            <h2>{subject}</h2>
                        </div>
                        <div class="content">
                            <p>Здравствуйте, {user.username.as_generic_type()}!</p>
                            <p>
                                Это письмо является подтверждением с
                                одноразовым паролем для авторизации на сайте it-call.
                            </p>
                            <p>Для завершения входа, перейдите по ссылке ниже:</p>
                            <p><a href="{self.confirm_url}?otp={otp}" class="button">Подтвердить вход</a></p>
                            <p>
                                <strong>
                                    Никому не сообщайте или не показывайте
                                    одноразовый пароль для вашей безопасности.
                                </strong>
                            </p>
                            <p>
                                <strong>
                                    Перейти по прямой ссылке:
                                    <a href="{self.confirm_url}?otp={otp}">{self.confirm_url}?otp={otp}</a>
                                </strong>
                            </p>
                        </div>
                        <div class="footer">
                            <p>© {datetime.now().year} it-call. Все права защищены.</p>
                        </div>
                    </div>
                </body>
            </html>
        """
        return body

    def build_message(self, user: UserEntity, otp: str) -> MIMEMultipart:
        subject = "Подтверждение одноразового пароля для сайта it-call"
        body = self.build_message_body(
            user=user,
            otp=otp,
            subject=subject,
        )

        msg = MIMEMultipart("alternative")
        msg["From"] = self.sender_mail
        msg["To"] = user.email.as_generic_type()
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        return msg

    def send_otp(self, user: UserEntity, otp: str) -> None:
        self.server.starttls()
        self.login()

        msg = self.build_message(user, otp)

        try:
            self.server.sendmail(
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
        finally:
            self.server.quit()
