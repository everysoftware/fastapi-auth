from typing import Annotated

from fastapi import Depends, APIRouter
from starlette import status

from app.db.schemas import PageParams, Page
from app.users.auth import AuthorizationForm
from app.users.dependencies import (
    UserServiceDep,
    UserDep,
    get_user,
    GetCurrentUser,
)
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
    users: UserServiceDep,
    user: UserCreate,
) -> UserRead:
    return await users.register(user)


@auth_router.post("/token", status_code=status.HTTP_200_OK)
async def login(
    users: UserServiceDep,
    form: Annotated[AuthorizationForm, Depends()],
) -> BearerToken:
    return await users.authorize(form)


#
# if google_sso:
#
#     @auth_router.get("/google/login")
#     async def google_login():
#         with google_sso:
#             return await google_sso.get_login_redirect()
#
#     @auth_router.get("/google/callback")
#     async def google_callback(request: Request):
#         with google_sso:
#             user = await google_sso.verify_and_process(request)
#         return user
#
#
# if yandex_sso:
#
#     @auth_router.get("/yandex/login")
#     async def yandex_login():
#         with yandex_sso:
#             return await yandex_sso.get_login_redirect()
#
#     @auth_router.get("/yandex/callback")
#     async def yandex_callback(request: Request):
#         with yandex_sso:
#             user = await yandex_sso.verify_and_process(request)
#         return user


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
