from fastapi import APIRouter, Query
from starlette import status

from app.users.dependencies import UserDep, UserServiceDep
from app.users.schemas import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", status_code=status.HTTP_200_OK)
def me(user: UserDep) -> UserRead:
    return user


@router.patch("/me", status_code=status.HTTP_200_OK)
async def patch(
    service: UserServiceDep,
    user: UserDep,
    update: UserUpdate,
    verify_token: str | None = Query(None),
) -> UserRead:
    return await service.update(user, update, verify_token)


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete(service: UserServiceDep, user: UserDep) -> UserRead:
    return await service.delete(user)
