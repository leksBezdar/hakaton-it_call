from dataclasses import dataclass, field
import hashlib
import re

from domain.exceptions.users import (
    EmptyEmail,
    EmptyPassword,
    EmptyUsername,
    InvalidEmailFormat,
    InvalidPasswordLength,
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
class Password(BaseValueObject):
    value: str
    is_hashed: bool = field(default=False, kw_only=True)

    def __post_init__(self):
        super().__post_init__()
        if not self.is_hashed:
            self.hash_password(self.value)

    def validate(self):
        if not self.value:
            raise EmptyPassword()

        value_length = len(self.value)

        if value_length not in range(3, 100):
            raise InvalidPasswordLength(value_length)

    def hash_password(self, password: str) -> None:
        self.is_hashed = True
        self.value = hashlib.sha256(password.encode("utf-8")).hexdigest()

    def check_password(self, plain_password: str) -> bool:
        hashed_input = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        return hashed_input == self.value

    def as_generic_type(self):
        return str(self.value)
