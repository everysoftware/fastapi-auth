from typing import AsyncGenerator, Annotated

from fastapi import Depends

from app.db.connection import async_session_factory
from app.db.uow import UOW

uow = UOW(async_session_factory)


async def get_uow() -> AsyncGenerator[UOW, None]:
    async with uow:
        yield uow


UOWDep = Annotated[UOW, Depends(get_uow)]
