# https://github.com/aiogram/aiogram/blob/dev-3.x/tests/conftest.py
import uuid

import pytest
import pytest_asyncio
from alembic.command import upgrade as alembic_upgrade
from alembic.script import ScriptDirectory
from sqlalchemy import make_url

from app.database import BaseOrm
from app.database.connection import (
    async_engine_factory,
    get_async_session_factory,
)
from app.settings import settings
from tests.utils.alchemy import create_database_async, drop_database_async
from tests.utils.alembic import alembic_config_from_url
from tests.utils.uow import TestUOW


@pytest_asyncio.fixture(scope="session")
async def database_dsn():
    url = make_url(settings.db_dsn)
    temp_db = f"test_{uuid.uuid4().hex}"
    url = url.set(database=temp_db)
    await create_database_async(url)
    yield url.render_as_string(hide_password=False)
    await drop_database_async(url)


@pytest.fixture(scope="session")
def alembic_config(database_dsn):
    return alembic_config_from_url(database_dsn)


@pytest.fixture(scope="session")
def run_migrations(alembic_config):
    revisions_dir = ScriptDirectory.from_config(alembic_config)
    if revisions_dir.get_current_head():
        alembic_upgrade(alembic_config, revisions_dir.get_current_head())


@pytest.fixture(scope="session")
def engine(run_migrations, database_dsn):
    return async_engine_factory(database_dsn)


@pytest.fixture(scope="session")
def session_factory(engine):
    return get_async_session_factory(engine)


async def delete_all(engine):
    async with engine.connect() as conn:
        for table in reversed(BaseOrm.metadata.sorted_tables):
            # Clean tables in such order that tables which depend on another go first
            await conn.execute(table.delete())
        await conn.commit()


@pytest_asyncio.fixture
async def session(session_factory):
    async with session_factory() as session:
        yield session

    await delete_all(session.bind)


@pytest_asyncio.fixture
async def uow(engine, session_factory):
    async with TestUOW(session_factory) as test_uow:
        yield test_uow

    await delete_all(engine)
