from dataclasses import dataclass, field
from typing import Iterable
from domain.entities.users import UserEntity
from domain.values.users import Username
from infrastructure.repositories.users.base import IUserRepository
from infrastructure.repositories.users.filters.users import GetUsersFilters


@dataclass
class InMemoryUserRepository(IUserRepository):
    _saved_users: list[UserEntity] = field(default_factory=list, kw_only=True)

    async def add(self, user: UserEntity) -> None:
        self._saved_users.append(user)

    async def get_by_oid(self, oid: str) -> UserEntity | None:
        for user in self._saved_users:
            if user.oid == oid:
                return user

    async def get_existing_usernames(self) -> list[Username]:
        return [user.username for user in self._saved_users]

    async def check_user_exists_by_email_and_username(
        self, email: str, username: str
    ) -> bool:
        return any(
            user.email == email or user.username == username
            for user in self._saved_users
        )

    async def get_all(
        self, filters: GetUsersFilters
    ) -> tuple[Iterable[UserEntity], int]:
        total_count = len(self._saved_users)
        limited_users = self._saved_users[
            filters.offset : filters.offset + filters.limit
        ]
        return limited_users, total_count

    async def update(self, user: UserEntity) -> UserEntity:
        for i, u in enumerate(self._saved_users):
            if u.oid == user.oid:
                self._saved_users[i] = user
                return user

    async def delete(self, oid: str) -> UserEntity | None:
        for user in self._saved_users:
            if user.oid == oid:
                self._saved_users.remove(user)
                return user
