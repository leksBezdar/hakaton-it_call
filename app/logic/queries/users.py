from collections.abc import Iterable
from dataclasses import dataclass, field

from domain.entities.users import UserEntity
from infrastructure.repositories.users.base import (
    IUserRepository,
)
from infrastructure.repositories.users.filters.users import (
    GetUsersFilters,
)
from infrastructure.security.cookies.base import ICookieManager
from logic.exceptions.users import UserNotFoundException
from logic.queries.base import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetUsersQuery(BaseQuery):
    filters: GetUsersFilters


@dataclass(frozen=True)
class GetUsersQueryHandler(BaseQueryHandler):
    user_repository: IUserRepository

    async def handle(self, query: GetUsersQuery) -> Iterable[UserEntity]:
        return await self.user_repository.get_all(filters=query.filters)


@dataclass
class Tokens:
    access_token: str
    refresh_token: str
    token_type: str = field(default="Bearer", kw_only=True)


@dataclass(frozen=True)
class GetTokensQuery(BaseQuery):
    user_oid: str


@dataclass(frozen=True)
class GetTokensQueryHandler(BaseQueryHandler):
    cookie_manager: ICookieManager
    user_repository: IUserRepository

    async def handle(self, query: GetTokensQuery) -> Tokens:
        access_token = await self.cookie_manager.create_access_token(query.user_oid)
        refresh_token = await self.cookie_manager.create_refresh_token(query.user_oid)

        return Tokens(access_token=access_token, refresh_token=refresh_token)


@dataclass(frozen=True)
class GetUserByIdQuery(BaseQuery):
    user_oid: str


@dataclass(frozen=True)
class GetUserByIdQueryHandler(BaseQueryHandler):
    user_repository: IUserRepository

    async def handle(self, query: GetUserByIdQuery) -> UserEntity:
        user = await self.user_repository.get_by_oid(oid=query.user_oid)
        if not user:
            raise UserNotFoundException(value=query.user_oid)

        return user


@dataclass(frozen=True)
class GetUserByUsernameQuery(BaseQuery):
    username: str


@dataclass(frozen=True)
class GetUserByUsernameQueryHandler(BaseQueryHandler):
    user_repository: IUserRepository

    async def handle(self, query: GetUserByUsernameQuery) -> UserEntity:
        user = await self.user_repository.get_by_username(username=query.username)
        if not user:
            raise UserNotFoundException(value=query.username)

        return user
