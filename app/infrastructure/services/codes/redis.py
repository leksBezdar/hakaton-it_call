from dataclasses import dataclass
from random import randint
from typing import Union

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
        user_email = user.email.as_generic_type()
        code = str(randint(10**5, 10**6 - 1))
        self.redis_client.set(user_email, code)

        return code

    def validate(self, code: str, user: UserEntity) -> None:
        # TODO move exception handling to command layer
        user_email = user.email.as_generic_type()
        cached_code: Union[bytes, None] = self.redis_client.get(user_email)

        if cached_code is None:
            raise CodeWasNotFoundException(code=code)

        decoded_cached_code = cached_code.decode("utf-8")
        if decoded_cached_code != code:
            raise CodesAreNotEqualException(
                code=code,
                cached_code=decoded_cached_code,
                user_email=user_email,
            )

        self.redis_client.delete(user_email)
