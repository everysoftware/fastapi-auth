import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, cast, Any

import sqlalchemy as sa
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy_utils.functions.database import _set_url_database
from sqlalchemy_utils.functions.database import (
    make_url,
)
from sqlalchemy_utils.functions.orm import quote

from app.db import BaseOrm


# Next functions are copied from `sqlalchemy_utils` and slightly
# modified to support async.
async def create_database_async(
    url: URL, encoding: str = "utf8", template: Optional[str] = None
) -> None:
    url = make_url(url)
    database = url.database
    dialect_name = url.get_dialect().name
    dialect_driver = url.get_dialect().driver

    if dialect_name == "postgresql":
        url = _set_url_database(url, database="postgres")
    elif dialect_name == "mssql":
        url = _set_url_database(url, database="master")
    elif dialect_name == "cockroachdb":
        url = _set_url_database(url, database="defaultdb")
    elif not dialect_name == "sqlite":
        url = _set_url_database(url, database=None)

    if (
        dialect_name == "mssql" and dialect_driver in {"pymssql", "pyodbc"}
    ) or (
        dialect_name == "postgresql"
        and dialect_driver in {"asyncpg", "pg8000", "psycopg2", "psycopg2cffi"}
    ):
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    else:
        engine = create_async_engine(url)

    if dialect_name == "postgresql":
        if not template:
            template = "template1"

        async with engine.begin() as conn:
            text = "CREATE DATABASE {} ENCODING '{}' TEMPLATE {}".format(
                quote(conn, database), encoding, quote(conn, template)
            )
            await conn.execute(sa.text(text))

    elif dialect_name == "mysql":
        async with engine.begin() as conn:
            text = "CREATE DATABASE {} CHARACTER SET = '{}'".format(
                quote(conn, database), encoding
            )
            await conn.execute(sa.text(text))

    elif dialect_name == "sqlite" and database != ":memory:":
        if database:
            async with engine.begin() as conn:
                await conn.execute(sa.text("CREATE TABLE DB(id int)"))
                await conn.execute(sa.text("DROP TABLE DB"))

    else:
        async with engine.begin() as conn:
            text = f"CREATE DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))

    await engine.dispose()


async def drop_database_async(url: URL) -> None:
    url = make_url(url)
    database = url.database
    dialect_name = url.get_dialect().name
    dialect_driver = url.get_dialect().driver

    if dialect_name == "postgresql":
        url = _set_url_database(url, database="postgres")
    elif dialect_name == "mssql":
        url = _set_url_database(url, database="master")
    elif dialect_name == "cockroachdb":
        url = _set_url_database(url, database="defaultdb")
    elif not dialect_name == "sqlite":
        url = _set_url_database(url, database=None)

    if dialect_name == "mssql" and dialect_driver in {"pymssql", "pyodbc"}:
        engine = create_async_engine(url, connect_args={"autocommit": True})
    elif dialect_name == "postgresql" and dialect_driver in {
        "asyncpg",
        "pg8000",
        "psycopg2",
        "psycopg2cffi",
    }:
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    else:
        engine = create_async_engine(url)

    if dialect_name == "sqlite" and database != ":memory:":
        if database:
            os.remove(database)
    elif dialect_name == "postgresql":
        async with engine.begin() as conn:
            # Disconnect all users from the database we are dropping.
            version = conn.dialect.server_version_info
            pid_column = "pid" if (version >= (9, 2)) else "procpid"  # type: ignore[operator]
            text = """
            SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}'
            AND {pid_column} <> pg_backend_pid();
            """.format(pid_column=pid_column, database=database)
            await conn.execute(sa.text(text))

            # Drop the database.
            text = f"DROP DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))
    else:
        async with engine.begin() as conn:
            text = f"DROP DATABASE {quote(conn, database)}"
            await conn.execute(sa.text(text))

    await engine.dispose()


async def delete_all(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        for table in reversed(BaseOrm.metadata.sorted_tables):
            # Clean tables in such order that tables which depend on another go first
            await conn.execute(table.delete())
        await conn.commit()


def get_test_db_url(template_url: str) -> URL:
    url = make_url(template_url)
    temp_db = f"test_{uuid.uuid4().hex}"
    url = url.set(database=temp_db)
    return cast(URL, url)


@asynccontextmanager
async def temporary_db(db_url: URL) -> AsyncGenerator[None, Any]:
    await create_database_async(db_url)
    yield
    await drop_database_async(db_url)
