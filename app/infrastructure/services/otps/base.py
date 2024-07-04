from abc import ABC, abstractmethod
from dataclasses import dataclass

import redis

from domain.entities.users import UserEntity


class IOTPService(ABC):
    @abstractmethod
    def generate_otp(self, user: UserEntity) -> str: ...

    @abstractmethod
    def validate(self, otp: str, user: UserEntity) -> None: ...


@dataclass(frozen=True)
class IRedisClient(ABC):
    redis_client: redis.Redis
