from dataclasses import dataclass
from random import randint
from typing import Union

from domain.entities.users import UserEntity
from domain.exceptions.otps import (
    OTPWasNotFoundException,
    OTPsAreNotEqualException,
)
from infrastructure.services.otps.base import IOTPService, IRedisClient


@dataclass(frozen=True)
class RedisOTPService(IOTPService, IRedisClient):
    async def generate_otp(self, user: UserEntity) -> str:
        user_email = user.email.as_generic_type()
        otp = str(randint(10**5, 10**6 - 1))
        await self.redis_client.set(user_email, otp)

        return otp

    async def validate(self, otp: str, user: UserEntity) -> None:
        user_email = user.email.as_generic_type()
        cached_otp: Union[bytes, None] = await self.redis_client.get(user_email)

        if cached_otp is None:
            raise OTPWasNotFoundException(otp=otp)

        decoded_cached_otp = cached_otp.decode("utf-8")
        if decoded_cached_otp != otp:
            raise OTPsAreNotEqualException(
                otp=otp,
                cached_otp=decoded_cached_otp,
                user_email=user_email,
            )

        await self.redis_client.delete(user_email)
