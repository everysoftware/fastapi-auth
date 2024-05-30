from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Self, cast

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class AbstractUOW(ABC):
    @property
    @abstractmethod
    def is_opened(self) -> bool:
        pass

    @abstractmethod
    async def open(self) -> None:
        pass

    @abstractmethod
    async def close(self, type_: Any, value: Any, traceback: Any) -> None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    async def __aenter__(self) -> Self:
        await self.open()

        return self

    async def __aexit__(self, type_: Any, value: Any, traceback: Any) -> None:
        await self.rollback()

        await self.close(type_, value, traceback)


class BaseUOW(AbstractUOW):
    """
    Base class for UOW.

    Usage::

        class UOW(BaseUOW):
            users: UserRepository

            async def on_open(self) -> None:
                self.users = UserRepository(self.session)


        async with UOW(session_factory) as uow:
            # TRANSACTION IS BEGUN...

            uow.users.add(User(name="Bob", age="18"))
            uow.commit()

    """  # noqa: E501

    session_factory: async_sessionmaker[AsyncSession]
    session: AsyncSession

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @property
    def is_opened(self) -> bool:
        if not self.session:
            return False

        return cast(bool, self.session.is_active)

    async def on_open(self) -> None: ...

    async def open(self) -> None:
        self.session = self.session_factory()
        await self.session.__aenter__()
        await self.on_open()

    async def close(self, type_: Any, value: Any, traceback: Any) -> None:
        await self.session.__aexit__(type_, value, traceback)

    async def flush(self) -> None:
        await self.session.flush()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def commit(self) -> None:
        await self.session.commit()
