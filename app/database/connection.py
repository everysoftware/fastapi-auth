from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)

from app.settings import settings


def async_engine_factory(dsn: str) -> AsyncEngine:
    return create_async_engine(dsn, echo=True)


def get_async_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async_engine = async_engine_factory(settings.db_dsn)
async_session_factory = get_async_session_factory(async_engine)
