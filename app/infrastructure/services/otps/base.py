from abc import ABC, abstractmethod
from dataclasses import dataclass

from redis import asyncio as aioredis

from domain.entities.users import UserEntity


class IOTPService(ABC):
    @abstractmethod
    async def generate_otp(self, user: UserEntity) -> str: ...

    @abstractmethod
    async def validate(self, otp: str, user: UserEntity) -> None: ...


@dataclass(frozen=True)
class IRedisClient(ABC):
    redis_client: aioredis.Redis
