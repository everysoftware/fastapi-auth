from typing import Annotated

from fastapi import HTTPException, Depends
from starlette import status

from app.db.types import ID
from app.dependencies import UOWDep
from app.permissions.service import PermissionService


def get_permission_service(
    uow: UOWDep,
) -> PermissionService:
    return PermissionService(uow)


PermissionServiceDep = Annotated[
    PermissionService, Depends(get_permission_service)
]


async def get_permission(permissions: PermissionServiceDep, permission_id: ID):
    permission = await permissions.get(permission_id)
    if permission is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Permission does not exist"
        )
    return permission
