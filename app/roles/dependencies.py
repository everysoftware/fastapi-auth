from typing import Annotated

from fastapi import HTTPException, Depends
from starlette import status

from app.database.types import ID
from app.dependencies import UOWDep
from app.roles.service import RoleService


def get_role_service(
    uow: UOWDep,
) -> RoleService:
    return RoleService(uow)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]


async def get_role(service: RoleServiceDep, role_id: ID):
    role = await service.get(role_id)
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role does not exist")
    return role
