from dataclasses import dataclass
import random

from domain.entities.users import UserEntity
from domain.exceptions.verification_tokens import (
    CodeWasNotFoundException,
    CodesAreNotEqualException,
)
from infrastructure.services.codes.base import ICodeService, IRedisClient


@dataclass(frozen=True)
class RedisCodeService(ICodeService, IRedisClient):
    # TODO replace redis with aioredis (redis.asyncio)
    def generate_code(self, user: UserEntity) -> str:
        # TODO replace random.randint code with a generated, user-binded token
        code = str(random.randint(10**5, 10**6 - 1))
        self.redis_client.set(user.email.as_generic_type(), code)

        return code

    def validate(self, code: str, user: UserEntity) -> None:
        cached_code: bytes = self.redis_client.get(user.email.as_generic_type())
        # TODO move exception handling to command layer
        if cached_code is None:
            raise CodeWasNotFoundException(code=code)

        if cached_code.decode("utf-8") != code:
            raise CodesAreNotEqualException(
                code=code,
                cached_code=cached_code.decode("utf-8"),
                user_email=user.email.as_generic_type(),
            )

        self.redis_client.delete(user.email.as_generic_type())
