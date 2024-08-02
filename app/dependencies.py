from typing import AsyncGenerator, Annotated

from fastapi import Depends

from app.database.connection import async_session_factory
from app.database.uow import UOW


async def get_uow() -> AsyncGenerator[UOW, None]:
    async with UOW(async_session_factory) as uow:
        yield uow


UOWDep = Annotated[UOW, Depends(get_uow)]
