from dataclasses import dataclass
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from smtplib import SMTP
from email.mime.text import MIMEText

from infrastructure.repositories.users.base import IUserRepository
from infrastructure.scheduler.base import IScheduler


# TODO: replace smtplib with aiosmtplib
@dataclass
class EmailScheduler(IScheduler):
    # TODO: Create base SMTP connector
    sender_mail: str
    smtp_app_password: str
    server: SMTP
    user_repository: IUserRepository

    # TODO: Replace with the real letter implementation; Decompose methods
    def send_email(self, to_email):
        subject = "Рассылка с напоминанием"

        msg = MIMEText("Hello! This is your daily greeting")
        msg["From"] = self.sender_mail
        msg["To"] = to_email
        msg["Subject"] = subject

        self.server.starttls()
        self.server.login(
            user=self.sender_mail,
            password=self.smtp_app_password,
        )
        self.server.sendmail(
            from_addr=self.sender_mail,
            to_addrs=to_email,
            msg=msg.as_string(),
        )

    async def send_daily_greetings(self):
        users = await self.user_repository.get_all_subscribed()
        for user in users:
            self.send_email(user.email.as_generic_type())

    async def start(self):
        self.scheduler = AsyncIOScheduler()
        # TODO: move time mark to .env; Bind tz to user tz
        self.scheduler.add_job(self.send_daily_greetings, "cron", hour=7, minute=0)
        self.scheduler.start()

    async def stop(self):
        self.scheduler.shutdown()
