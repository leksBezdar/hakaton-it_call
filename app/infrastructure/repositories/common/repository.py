from abc import ABC
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.models.common.base import Base
from infrastructure.repositories.common.database import async_session, test_session
from settings.settings import Settings


class ISqlalchemyRepository(ABC):
    _model: type[Base] = NotImplemented
    _session_factory: Callable = async_session

    def __init__(self) -> None:
        test_mode = Settings.TEST_MODE
        if test_mode:
            self._session_factory = test_session

    def get_session(self) -> AsyncSession:
        return self._session_factory()

    @property
    def model_fields(self):
        return self._model.__table__.columns
