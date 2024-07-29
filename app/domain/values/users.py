from dataclasses import dataclass
import re

from pytz import timezone
from pytz.tzinfo import DstTzInfo

from domain.exceptions.users import (
    EmptyEmail,
    EmptyTimezone,
    EmptyUsername,
    InvalidEmailFormat,
    InvalidUsernameCharacters,
    InvalidUsernameLength,
)
from domain.values.base import BaseValueObject


@dataclass
class Username(BaseValueObject):
    value: str

    def validate(self) -> None:
        if not self.value:
            raise EmptyUsername()

        value_length = len(self.value)

        if value_length not in range(3, 16):
            raise InvalidUsernameLength(self.value)

        if not re.match(r"^[a-zA-Z0-9_*\\-]+$", self.value):
            raise InvalidUsernameCharacters(self.value)

    def as_generic_type(self) -> str:
        return str(self.value)


@dataclass
class UserEmail(BaseValueObject):
    value: str

    def __post_init__(self):
        return super().__post_init__()

    def validate(self):
        if not self.value:
            raise EmptyEmail()

        if not re.match(r"^\S+@\S+\.\S+$", self.value):
            raise InvalidEmailFormat(self.value)

    def as_generic_type(self):
        return str(self.value)


@dataclass
class UserTimezone(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyTimezone()

    def as_generic_type(self):
        return str(self.value)

    def as_timezone_type(self) -> DstTzInfo:
        return timezone(zone=self.value)
