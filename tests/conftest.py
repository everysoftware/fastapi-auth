# https://github.com/aiogram/aiogram/blob/dev-3.x/tests/conftest.py
import uuid

import pytest
import pytest_asyncio
from alembic.command import upgrade as alembic_upgrade
from alembic.script import ScriptDirectory
from sqlalchemy_utils import create_database, drop_database
from starlette.testclient import TestClient

from tests.utils.alembic import alembic_config_from_url
from tests.utils.uow import TestUOW
from app.settings import settings
from fastabc import DeclarativeBase
from app.database.connection import (
    async_engine_factory,
    get_async_session_factory,
)
from app import app


@pytest.fixture(scope="session")
def database_dsn():
    tmp_db_name = f"__test_{uuid.uuid4().hex}__"
    tmp_db_url = settings.db.get_dsn(tmp_db_name)
    async_tmp_db_url = settings.db.get_dsn(tmp_db_name, sync=False)

    create_database(tmp_db_url)
    yield async_tmp_db_url
    drop_database(tmp_db_url)


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
        for table in reversed(DeclarativeBase.metadata.sorted_tables):
            # Clean tables in such order that tables which depend on another go first
            await conn.execute(table.delete())
        await conn.commit()


@pytest_asyncio.fixture
async def active_session(session_factory):
    async with session_factory() as session:
        yield session

    await delete_all(session.bind)


@pytest_asyncio.fixture
async def uow(engine, session_factory):
    async with TestUOW(session_factory) as test_uow:
        yield test_uow

    await delete_all(engine)


@pytest.fixture(scope="session")
def client():
    return TestClient(app)
