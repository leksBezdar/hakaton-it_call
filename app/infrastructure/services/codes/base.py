from abc import ABC, abstractmethod
from dataclasses import dataclass

import redis

from domain.entities.users import UserEntity


class ICodeSerivce(ABC):
    @abstractmethod
    def generate_code(self, user: UserEntity) -> str: ...

    @abstractmethod
    def validate(self, code: str, user: UserEntity) -> None: ...


@dataclass(frozen=True)
class IRedisClient(ABC):
    redis_client: redis.Redis
