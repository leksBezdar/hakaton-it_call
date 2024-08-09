from dataclasses import dataclass
from datetime import datetime


from infrastructure.services.smtp.mails.base import IMessage
from domain.entities.users import UserEntity


@dataclass
class ReminderMessage(IMessage):
    user: UserEntity
    main_page_url: str
    unsubscribe_url: str

    @property
    def subject(self) -> str:
        return "Ежедневное напоминание"

    @property
    def body(self) -> str:
        current_datetime = datetime.now(
            self.user.user_timezone.as_timezone_type()
        ).strftime("%d.%m.%Y %H:%M")

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
                            <h2>{self.subject}</h2>
                        </div>
                        <div class="content">
                            <p>Здравствуйте, {self.user.username.as_generic_type()}!</p>
                            <p>
                                Это ваше ежедневное напоминание о новых доступных и
                                пропущенных рекомендациях.
                            </p>
                            <p>Чтобы просмотреть все рекомендации, перейдите по ссылке ниже:</p>
                            <p><a href="{self.main_page_url}" class="button">Просмотреть рекомендации</a></p>
                        </div>
                        <div class="footer">
                            <p>С уважением, команда it-call. Время отправки письма: {current_datetime}</p>
                            <p>© {datetime.now().year} it-call. Все права защищены.</p>
                            <p>
                                <a href="{self.unsubscribe_url}{self.user.oid}">
                                    Отписаться от рассылки
                                </a>
                            </p>
                        </div>
                    </div>
                </body>
            </html>
        """
        return body
