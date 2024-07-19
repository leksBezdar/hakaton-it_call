from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Iterable

from sqlalchemy import Select, func, or_, select

from domain.entities.users import UserEntity
from infrastructure.repositories.common.exception_mapper import exception_mapper
from infrastructure.models.users import UserModel
from infrastructure.repositories.common.repository import ISqlalchemyRepository
from infrastructure.repositories.users.base import (
    IUserRepository,
)
from infrastructure.repositories.users.converters import (
    convert_user_entity_to_model,
    convert_user_model_to_entity,
)
from infrastructure.repositories.users.filters.users import GetUsersFilters


@dataclass(frozen=True)
class SqlAlchemyUserRepository(IUserRepository, ISqlalchemyRepository):
    _model: type[UserModel] = UserModel

    @exception_mapper
    async def add(self, user: UserEntity) -> None:
        user_model = convert_user_entity_to_model(user)
        async with self.get_session() as session:
            session.add(user_model)
            await session.commit()

    @exception_mapper
    async def get_by_oid(self, oid: str) -> UserEntity | None:
        async with self.get_session() as session:
            result = await session.execute(select(self._model).filter_by(oid=oid))
            user = result.scalars().first()

            return convert_user_model_to_entity(user) if user else None

    @exception_mapper
    async def get_by_email(self, email: str) -> UserEntity | None:
        async with self.get_session() as session:
            result = await session.execute(select(self._model).filter_by(email=email))
            user = result.scalars().first()

            return convert_user_model_to_entity(user) if user else None

    @exception_mapper
    async def check_user_exists_by_email_and_username(
        self, email: str, username: str
    ) -> bool:
        async with self.get_session() as session:
            result = await session.execute(
                select(self._model).filter(
                    or_(self._model.email == email, self._model.username == username)
                )
            )
            return result.scalars().first() is not None

    @exception_mapper
    async def get_all(
        self, filters: GetUsersFilters
    ) -> tuple[Iterable[UserEntity], int]:
        async with self.get_session() as session:
            get_users_query = await self._build_get_users_query(filters)
            count_users_query = await self._build_count_users_query(filters)

            get_users_result = await session.execute(get_users_query)
            count_result = await session.execute(count_users_query)

            count = count_result.scalar()
            users = get_users_result.scalars().all()

            users = [convert_user_model_to_entity(user) for user in users]
            return users, count

    @exception_mapper
    async def get_all_subscribed(self) -> list[UserEntity]:
        async with self.get_session() as session:
            result = await session.execute(
                select(self._model).filter_by(is_subscribed=True)
            )
            users = result.scalars().all()

            return [convert_user_model_to_entity(user) for user in users]

    @exception_mapper
    async def get_existing_usernames(self) -> list[str]:
        async with self.get_session() as session:
            return await session.scalars(
                select(self._model.username).where(self._model.username.is_not(None))
            )

    @exception_mapper
    async def update(self, user: UserEntity) -> UserEntity:
        async with self.get_session() as session:
            user_model = convert_user_entity_to_model(user)
            await session.merge(user_model)
            await session.commit()

            return convert_user_model_to_entity(user_model)

    @exception_mapper
    async def restore(self, user: UserEntity) -> None:
        async with self.get_session() as session:
            user_model = convert_user_entity_to_model(user)

            user_model.is_deleted = False
            user_model.deleted_at = None
            await session.merge(user_model)
            await session.commit()

    @exception_mapper
    async def delete(self, oid: str) -> UserEntity | None:
        async with self.get_session() as session:
            result = await session.execute(select(self._model).filter_by(oid=oid))
            user = result.scalars().first()
            if user:
                user.is_deleted = True
                user.deleted_at = datetime.now(UTC)
                await session.commit()

                return convert_user_model_to_entity(user)

    async def _build_get_users_query(self, filters: GetUsersFilters) -> Select:
        query = select(self._model).limit(filters.limit).offset(filters.offset)
        query = await self._apply_filters(query, filters)

        return query

    async def _build_count_users_query(self, filters: GetUsersFilters) -> Select:
        query = select(func.count()).select_from(self._model)
        query = await self._apply_filters(query, filters)

        return query

    async def _apply_filters(self, query: Select, filters: GetUsersFilters) -> Select:
        if not filters.show_deleted:
            query = query.where(self._model.is_deleted == filters.show_deleted)

        return query
