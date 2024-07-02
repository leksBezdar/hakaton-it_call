from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from domain.events.base import BaseEvent


@dataclass
class UserCreatedEvent(BaseEvent):
    title: ClassVar[str] = "New User Created"

    username: str
    user_oid: str
    email: str
    is_subscribed: bool


@dataclass
class UserChangedUsernameEvent(BaseEvent):
    title: ClassVar[str] = "Username Changed"

    user_oid: str
    old_username: str
    new_username: str


@dataclass
class UserChangedPasswordEvent(BaseEvent):
    title: ClassVar[str] = "Password Changed"

    user_oid: str


@dataclass
class UserSubscribedToEmailSenderEvent(BaseEvent):
    title: ClassVar[str] = "User Subscribed to Email Sender"

    user_oid: str
    username: str
    email: str


@dataclass
class UserUnsubscribedFromEmailSenderEvent(BaseEvent):
    title: ClassVar[str] = "User Unsubscribed from Email Sender"

    user_oid: str
    username: str
    email: str


@dataclass
class RestoreUserEvent(BaseEvent):
    title: ClassVar[str] = "User was restored"

    user_oid: str
    username: str
    restore_datetime: datetime


@dataclass
class UserDeletedEvent(BaseEvent):
    title: ClassVar[str] = "User was deleted"

    user_oid: str
    username: str
    email: str
