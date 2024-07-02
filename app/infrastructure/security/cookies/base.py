from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ICookieManager(ABC):
    _token_secret_key: str
    _algorithm: str
    _access_token_expire_minutes: int
    _refresh_token_expire_days: int

    @abstractmethod
    async def create_access_token(self, user_oid: str) -> str:
        pass

    @abstractmethod
    async def create_refresh_token(self, user_oid: str) -> str:
        pass

    @abstractmethod
    async def get_payload(self, token: str) -> str:
        pass
