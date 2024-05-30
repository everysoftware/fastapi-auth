from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.skeleton.orm import AbstractUOW


class BaseMultipleUOW(AbstractUOW):
    """
    This UOW allows to work with multiple sessions.

    Usage::

        def get_session_factories() -> dict[str, async_sessionmaker[AsyncSession]]:
            engines = {
                "first-db": create_async_engine(
                    "postgresql+asyncpg://user:password@localhost/first_db"
                ),
                "second-db": create_async_engine(
                    "postgresql+asyncpg://user:password@localhost/second_db"
                ),
            }

            return {
                name: async_sessionmaker(engine)
                for name, engine in engines.items()
            }


        class UOW(BaseMultipleUOW):
            users: UserRepository
            music: MusicRepository

            async def open(self) -> None:
                self.users = UserRepository(self.sessions["first-db"])
                self.music = MusicRepository(self.sessions["second-db"])


        async with UOW(get_session_factories()) as uow:
            # TRANSACTION IS BEGUN...

            uow.users.add(User(name="Bob", age="18"))
            now.music.add(Music(name="Song", author="Bob"))

            uow.commit()

    """  # noqa: E501

    session_factories: dict[str, async_sessionmaker[AsyncSession]]
    sessions: dict[str, AsyncSession]

    def __init__(
        self, session_factories: dict[str, async_sessionmaker[AsyncSession]]
    ) -> None:
        self.session_factories = session_factories

    @property
    def is_opened(self) -> bool:
        if not self.sessions:
            return False

        return any(session.is_active for session in self.sessions.values())

    async def open(self) -> None:
        self.sessions = {
            name: factory() for name, factory in self.session_factories.items()
        }

        for session in self.sessions.values():
            await session.__aenter__()

    async def close(self, type_: Any, value: Any, traceback: Any) -> None:
        for session in self.sessions.values():
            await session.__aexit__(type_, value, traceback)

    async def flush(self) -> None:
        for session in self.sessions.values():
            await session.flush()

    async def commit(self) -> None:
        for session in self.sessions.values():
            await session.commit()

    async def rollback(self) -> None:
        for session in self.sessions.values():
            await session.rollback()
