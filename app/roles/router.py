from typing import Annotated

from fastapi import Depends, APIRouter

from app.database.schemas import PageParams, Page
from app.permissions.schemas import PermissionRead
from app.roles.dependencies import RoleServiceDep, get_role
from app.roles.schemas import RoleCreate, RoleRead, RoleUpdate

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/")
async def create(service: RoleServiceDep, creation: RoleCreate) -> RoleRead:
    return await service.create(creation)


@router.get("/{role_id}")
def get(role: Annotated[RoleRead, Depends(get_role)]) -> RoleRead:
    return role


@router.patch("/{role_id}")
async def patch(
    service: RoleServiceDep,
    role: Annotated[RoleRead, Depends(get_role)],
    update: RoleUpdate,
) -> RoleRead:
    return await service.update(role.id, update)


@router.delete("/{role_id}")
async def delete(
    service: RoleServiceDep, role: Annotated[RoleRead, Depends(get_role)]
) -> RoleRead:
    return await service.delete(role.id)


@router.get("/")
async def get_many(
    service: RoleServiceDep, params: Annotated[PageParams, Depends()]
) -> Page[PermissionRead]:
    return await service.get_many(params)
