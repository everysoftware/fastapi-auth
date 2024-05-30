from typing import AsyncGenerator, Annotated

from fastapi import Depends

from app.core import UOW, Gateway, UnauthorizedGateway
from app.database.connection import async_session_factory


async def get_uow() -> AsyncGenerator[UOW, None]:
    async with UOW(async_session_factory) as uow:
        yield uow


UOWDep = Annotated[UOW, Depends(get_uow)]


async def get_unauthorized_gateway(uow: UOWDep) -> UnauthorizedGateway:
    return UnauthorizedGateway(uow)


UGWDep = Annotated[UnauthorizedGateway, Depends(get_unauthorized_gateway)]


async def get_gateway(uow: UOWDep) -> Gateway:
    return Gateway(uow)


GWDep = Annotated[Gateway, Depends(get_gateway)]
