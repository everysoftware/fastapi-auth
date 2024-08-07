from typing import Annotated

from fastapi import Depends, APIRouter

from app.database.schemas import PageParams, Page
from app.permissions.dependencies import get_permission, PermissionServiceDep
from app.permissions.schemas import (
    PermissionRead,
    PermissionUpdate,
    PermissionCreate,
)

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("/")
async def create(
    service: PermissionServiceDep, creation: PermissionCreate
) -> PermissionRead:
    return await service.create(creation)


@router.get("/{permission_id}")
def get(
    permission: Annotated[PermissionRead, Depends(get_permission)],
) -> PermissionRead:
    return permission


@router.patch("/{permission_id}")
async def patch(
    service: PermissionServiceDep,
    permission: Annotated[PermissionRead, Depends(get_permission)],
    update: PermissionUpdate,
) -> PermissionRead:
    return await service.update(permission.id, update)


@router.delete("/{permission_id}")
async def delete(
    service: PermissionServiceDep,
    permission: Annotated[PermissionRead, Depends(get_permission)],
) -> PermissionRead:
    return await service.delete(permission.id)


@router.get("/")
async def get_many(
    service: PermissionServiceDep, params: Annotated[PageParams, Depends()]
) -> Page[PermissionRead]:
    return await service.get_many(params)
