from typing import AsyncGenerator, Any

import pytest
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.connection import (
    get_async_engine,
    get_async_session_factory,
)
from tests.utils.alembic import alembic_upgrade_head, alembic_config_from_url
from tests.utils.db import get_test_db_url, temporary_db, delete_all

test_db_url = get_test_db_url(settings.db_dsn)
test_engine = get_async_engine(test_db_url, poolclass=pool.NullPool)
test_factory = get_async_session_factory(test_engine)
alembic_config = alembic_config_from_url(test_db_url)


@pytest.fixture(scope="session", autouse=True)
async def init_db() -> AsyncGenerator[None, Any]:
    async with temporary_db(test_db_url):
        yield


@pytest.fixture(scope="session", autouse=True)
async def run_migrations() -> None:
    await alembic_upgrade_head(alembic_config)


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with test_factory() as session:
        yield session

    await delete_all(test_engine)
