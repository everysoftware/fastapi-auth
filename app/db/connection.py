from typing import Any

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)

from app.config import settings


def get_async_engine(dsn: str | URL, **kwargs: Any) -> AsyncEngine:
    return create_async_engine(dsn, echo=True, pool_pre_ping=True, **kwargs)


def get_async_session_factory(
    engine: AsyncEngine, **kwargs: Any
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, **kwargs)


async_engine = get_async_engine(settings.db.db_dsn)
async_session_factory = get_async_session_factory(async_engine)
