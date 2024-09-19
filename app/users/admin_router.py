from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.schemas import PageParams, Page
from app.users.dependencies import Requires, get_user_by_id, UserServiceDep
from app.users.schemas import UserRead, UserUpdate, Role

router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(Requires(is_superuser=True))],
)


@router.get("/users/{user_id}")
def get_by_id(user: Annotated[UserRead, Depends(get_user_by_id)]) -> UserRead:
    return user


@router.patch("/users/{user_id}")
async def update_by_id(
    service: UserServiceDep,
    user: Annotated[UserRead, Depends(get_user_by_id)],
    update: UserUpdate,
) -> UserRead:
    return await service.update(user, update)


@router.delete("/users/{user_id}")
async def delete_by_id(
    service: UserServiceDep, user: Annotated[UserRead, Depends(get_user_by_id)]
) -> UserRead:
    return await service.delete(user)


@router.get("/users/")
async def get_many(
    service: UserServiceDep, params: Annotated[PageParams, Depends()]
) -> Page[UserRead]:
    return await service.get_many(params)


@router.post("/users/{user_id}/grant")
async def grant(
    service: UserServiceDep,
    user: Annotated[UserRead, Depends(get_user_by_id)],
    role: Role = Role.user,
) -> UserRead:
    return await service.grant(user, role)
