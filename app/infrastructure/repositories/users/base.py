from abc import ABC, abstractmethod
from typing import Iterable

from domain.entities.users import UserEntity
from domain.values.users import Username
from infrastructure.repositories.users.filters.users import GetUsersFilters


class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user: UserEntity) -> None: ...

    @abstractmethod
    async def get_by_oid(self, oid: str) -> UserEntity | None: ...

    @abstractmethod
    async def get_existing_usernames(self) -> list[Username]: ...

    @abstractmethod
    async def check_user_exists_by_email_and_username(
        self, email: str, username: str
    ) -> bool: ...

    @abstractmethod
    async def get_all(
        self, filters: GetUsersFilters
    ) -> tuple[Iterable[UserEntity], int]: ...

    @abstractmethod
    async def restore(self, user: UserEntity) -> None: ...

    @abstractmethod
    async def update(self, user: UserEntity) -> UserEntity: ...

    @abstractmethod
    async def delete(self, oid: str) -> UserEntity | None: ...
