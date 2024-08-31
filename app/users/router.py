from typing import Annotated

from fastapi import Depends, APIRouter
from starlette import status

from app.db.schemas import PageParams, Page
from app.users.dependencies import (
    UserServiceDep,
    UserDep,
    get_user,
    GetCurrentUser,
)
from app.users.exceptions import InvalidGrantType
from app.users.oauth2 import CustomOAuth2PasswordRequestForm
from app.users.schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
    BearerToken,
    Role,
)

router = APIRouter()

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    auth: UserServiceDep,
    user: UserCreate,
) -> UserRead:
    return await auth.register(user)


@auth_router.post("/token", status_code=status.HTTP_200_OK)
async def login(
    users: UserServiceDep,
    form: Annotated[CustomOAuth2PasswordRequestForm, Depends()],
) -> BearerToken:
    match form.grant_type:
        case "password":
            assert form.username is not None
            assert form.password is not None
            token = await users.authorize_by_password(
                form.username, form.password
            )
        case "refresh_token":
            assert form.refresh_token is not None
            token = await users.authorize_by_refresh_token(form.refresh_token)
        case _:
            raise InvalidGrantType()
    return token


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/me", status_code=status.HTTP_200_OK)
def me(user: UserDep) -> UserRead:
    return user


@user_router.patch("/me", status_code=status.HTTP_200_OK)
async def patch(
    users: UserServiceDep, user: UserDep, update: UserUpdate
) -> UserRead:
    return await users.update(user.id, update)


@user_router.delete("/me", status_code=status.HTTP_200_OK)
async def delete(users: UserServiceDep, user: UserDep) -> UserRead:
    return await users.delete(user.id)


su_router = APIRouter(
    tags=["Admin"], dependencies=[Depends(GetCurrentUser(is_superuser=True))]
)


@su_router.get("/{user_id}")
def get_by_id(user: Annotated[UserRead, Depends(get_user)]) -> UserRead:
    return user


@su_router.patch("/{user_id}")
async def update_by_id(
    service: UserServiceDep,
    user: Annotated[UserRead, Depends(get_user)],
    update: UserUpdate,
) -> UserRead:
    return await service.update(user.id, update)


@su_router.delete("/{user_id}")
async def delete_by_id(
    service: UserServiceDep, user: Annotated[UserRead, Depends(get_user)]
) -> UserRead:
    return await service.delete(user.id)


@su_router.get("/")
async def get_many(
    service: UserServiceDep, params: Annotated[PageParams, Depends()]
) -> Page[UserRead]:
    return await service.get_many(params)


@su_router.post("/{user_id}/grant")
async def grant(
    service: UserServiceDep,
    user: Annotated[UserRead, Depends(get_user)],
    role: Role = Role.user,
) -> UserRead:
    return await service.grant(user.id, role)


user_router.include_router(su_router)
