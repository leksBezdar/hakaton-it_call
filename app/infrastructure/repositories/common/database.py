from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from infrastructure.repositories.common.db_convention import DB_NAMING_CONVENTION
from settings.settings import settings


metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


async_engine = create_async_engine(settings.DB_URL, echo=True)
test_async_engine = create_async_engine(settings.TEST_DB_URL)


async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)

test_session = async_sessionmaker(
    test_async_engine,
    expire_on_commit=False,
)
