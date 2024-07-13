from datetime import datetime
import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from pytz import all_timezones

from application.api.schemas import SBaseQueryResponse
from domain.entities.users import UserEntity


etc_timezones = [tz for tz in all_timezones if re.match(r"^Etc/GMT[\+-]\d+$", tz)]


class SCreateUserIn(BaseModel):
    email: EmailStr
    username: str
    user_timezone: str = Field(default="Etc/GMT+3")
    is_subscribed: bool = False

    @field_validator("user_timezone")
    def validate_timezone(cls, v):
        if v not in etc_timezones:
            raise ValueError(
                f"Часовой пояс должен быть одним из перечисленных: {etc_timezones}"
            )
        return v


class SCreateUserOut(BaseModel):
    oid: str
    email: EmailStr
    username: str
    created_at: datetime
    is_subscribed: bool

    @classmethod
    def from_entity(cls, user: UserEntity) -> "SCreateUserOut":
        return cls(
            oid=user.oid,
            email=user.email.as_generic_type(),
            username=user.username.as_generic_type(),
            created_at=user.created_at,
            is_subscribed=user.is_subscribed,
        )


class SLoginIn(BaseModel):
    email: EmailStr


class SLoginOut(BaseModel):
    message: str


class SConfirmIn(BaseModel):
    email: EmailStr
    otp: str


class SConfirmOut(BaseModel):
    oid: str
    email: EmailStr
    username: str
    created_at: datetime
    is_subscribed: bool

    @classmethod
    def from_entity(cls, user: UserEntity) -> "SConfirmOut":
        return cls(
            oid=user.oid,
            email=user.email.as_generic_type(),
            username=user.username.as_generic_type(),
            created_at=user.created_at,
            is_subscribed=user.is_subscribed,
        )


class SGetUser(BaseModel):
    oid: str
    email: EmailStr
    username: str
    created_at: datetime
    is_subscribed: bool

    @classmethod
    def from_entity(cls, user: UserEntity) -> "SGetUser":
        return cls(
            oid=user.oid,
            email=user.email.as_generic_type(),
            username=user.username.as_generic_type(),
            created_at=user.created_at,
            is_subscribed=user.is_subscribed,
        )


class SChangeUsername(BaseModel):
    new_username: str


class SGetUsersQueryResponse(SBaseQueryResponse[list[SGetUser]]): ...
