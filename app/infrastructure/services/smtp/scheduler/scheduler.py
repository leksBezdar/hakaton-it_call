from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import orjson
from pytz import utc

from domain.entities.users import UserEntity
from domain.values.users import UserEmail, UserTimezone, Username
from infrastructure.exceptions.senders import (
    SMTPDataError,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
)
from infrastructure.repositories.users.base import IUserRepository
from infrastructure.services.smtp.gmail import GmailSMTPClient
from infrastructure.services.smtp.mails.base import IMessage
from infrastructure.services.smtp.mails.reminders import ReminderMessage
from infrastructure.services.smtp.scheduler.base import IScheduler
from infrastructure.message_brokers.kafka import KafkaMessageBroker
from settings.settings import Settings


# TODO: replace with aiosmptlib implementation
@dataclass
class EmailScheduler(IScheduler, GmailSMTPClient):
    settings: Settings
    main_page_url: str
    user_repository: IUserRepository
    message_broker: KafkaMessageBroker
    user_jobs: dict[str, str] = None

    def __post_init__(self):
        self.user_jobs = {}

    def build_message(self, user: UserEntity) -> MIMEMultipart:
        # TODO: move out url to .env; use di
        unsubscribe_url: str = f"http://0.0.0.0:8000/users/{user.oid}/unsubscribe/"
        reminder_message: IMessage = ReminderMessage(
            user=user,
            unsubscribe_url=unsubscribe_url,
            main_page_url=self.main_page_url,
        )

        msg = MIMEMultipart("alternative")
        msg["From"] = self.sender_mail
        msg["To"] = user.email.as_generic_type()
        msg["Subject"] = reminder_message.subject
        msg.attach(MIMEText(reminder_message.body, "html"))

        return msg

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
                raise SMTPRecipientsRefused
            except smtplib.SMTPSenderRefused:
                raise SMTPSenderRefused
            except smtplib.SMTPDataError:
                raise SMTPDataError

    async def schedule_user_reminders(self, users: list[UserEntity]):
        for user in users:
            send_time = datetime.strptime(self.settings.SEND_TIME, "%H:%M")
            send_time_utc = utc.localize(send_time)
            user_tz = user.user_timezone.as_timezone_type()

            utc_time = send_time_utc + user_tz.utcoffset(send_time_utc)

            job = self.scheduler.add_job(
                self.send_reminder,
                trigger=CronTrigger(
                    hour=utc_time.hour,
                    minute=utc_time.minute,
                    timezone=utc,
                ),
                args=[user],
            )
            self.user_jobs[user.oid] = job.id

    def print_scheduled_jobs(self):
        for job in self.scheduler.get_jobs():
            print(
                f"Job ID: {job.id},"
                f"Next Run Time: {job.next_run_time},"
                f"Args: {job.args},"
                f"Trigger: {job.trigger},"
                f"Timezone: {job.trigger.timezone}"
            )

    async def _handle_user_subscribed(self, message):
        user_data = UserEntity(
            oid=message["user_oid"],
            email=UserEmail(value=message["email"]),
            username=Username(value=message["username"]),
            user_timezone=UserTimezone(value=message["user_timezone"]),
            is_subscribed=True,
        )
        await self.schedule_user_reminders([user_data])

    async def _handle_user_unsubscribed(self, message: dict) -> None:
        user_oid = message["user_oid"]
        if user_oid in self.user_jobs:
            self.scheduler.remove_job(self.user_jobs[user_oid])
            del self.user_jobs[user_oid]

    async def consume_user_event(self) -> None:
        self.message_broker.consumer.subscribe(
            topics=[
                self.settings.user_subscribed_event_topic,
                self.settings.user_unsubscribed_event_topic,
            ]
        )
        async for message in self.message_broker.consumer:
            topic = message.topic
            message = orjson.loads(message.value)

            if topic == self.settings.user_subscribed_event_topic:
                await self._handle_user_subscribed(message)
            elif topic == self.settings.user_unsubscribed_event_topic:
                await self._handle_user_unsubscribed(message)

    async def start(self):
        self.scheduler = AsyncIOScheduler()
        users = await self.user_repository.get_all_subscribed()
        await self.schedule_user_reminders(users)
        self.scheduler.start()
        self.scheduler.add_job(self.consume_user_event)

    async def stop(self):
        self.scheduler.shutdown()
