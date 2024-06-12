from typing import AsyncGenerator, Annotated

from fastapi import Depends

from app.core.gateway import Gateway
from app.core.uow import UOW
from app.database.connection import async_session_factory


async def get_uow() -> AsyncGenerator[UOW, None]:
    async with UOW(async_session_factory) as uow:
        yield uow


UOWDep = Annotated[UOW, Depends(get_uow)]


async def get_gateway(uow: UOWDep) -> Gateway:
    return Gateway(uow)


GWDep = Annotated[Gateway, Depends(get_gateway)]
