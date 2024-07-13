from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
import smtplib
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from email.mime.text import MIMEText

from domain.entities.users import UserEntity
from infrastructure.repositories.users.base import IUserRepository
from infrastructure.services.smtp.gmail import GmailSMTPClient
from infrastructure.services.smtp.mails.base import IMessage
from infrastructure.services.smtp.mails.reminders import ReminderMessage
from infrastructure.services.smtp.scheduler.base import IScheduler


# TODO: replace smtplib with aiosmtplib
@dataclass
class EmailScheduler(IScheduler, GmailSMTPClient):
    main_page_url: str
    user_repository: IUserRepository

    def build_message(self, user: UserEntity) -> MIMEMultipart:
        # TODO: move url to settings; Use di
        unsubcribe_url: str = f"http://0.0.0.0:8000/users/{user.oid}/unsubscribe/"
        reminder_message: IMessage = ReminderMessage(
            user=user,
            unsubscribe_url=unsubcribe_url,
            main_page_url=self.main_page_url,
        )

        msg = MIMEMultipart("alternative")
        msg["From"] = self.sender_mail
        msg["To"] = user.email.as_generic_type()
        msg["Subject"] = reminder_message.subject

        msg.attach(MIMEText(reminder_message.body, "html"))

        return msg

    # TODO: Replace with the real letter implementation; Decompose methods
    def send_reminder(self, user: UserEntity):
        with smtplib.SMTP(*self.smtp_url) as server:
            server.starttls()
            self.login(server)

            msg = self.build_message(user)

            try:
                server.sendmail(
                    from_addr=self.sender_mail,
                    to_addrs=user.email.as_generic_type(),
                    msg=msg.as_string(),
                )
            except smtplib.SMTPRecipientsRefused:
                raise smtplib.SMTPRecipientsRefused
            except smtplib.SMTPSenderRefused:
                raise smtplib.SMTPSenderRefused
            except smtplib.SMTPDataError:
                raise smtplib.SMTPDataError

    async def send_daily_reminder(self):
        users = await self.user_repository.get_all_subscribed()
        for user in users:
            self.send_reminder(user)

    async def start(self):
        self.scheduler = AsyncIOScheduler()
        # TODO: move time mark to .env; Bind tz to user tz
        self.scheduler.add_job(self.send_daily_reminder, "cron", hour=17, minute=35)
        self.scheduler.start()

    async def stop(self):
        self.scheduler.shutdown()
