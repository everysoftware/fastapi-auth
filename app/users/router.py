from typing import Annotated

from fastapi import Depends, APIRouter, Query, Cookie
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.db.schemas import PageParams, Page
from app.sso.base import SSOProvider
from app.sso.dependencies import get_sso
from app.sso.schemas import SSOCallback
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
    service: UserServiceDep,
    user: UserCreate,
) -> UserRead:
    return await service.register(user)


@auth_router.post("/token", status_code=status.HTTP_200_OK)
async def login(
    service: UserServiceDep,
    form: Annotated[AuthorizationForm, Depends()],
) -> BearerToken:
    return await service.authorize(form)


@auth_router.get("/{provider}", status_code=status.HTTP_303_SEE_OTHER)
async def sso_login(
    service: UserServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    redirect_uri: str | None = Query(None),
) -> RedirectResponse:
    login_url = await service.sso_login(provider, redirect_uri)
    response = RedirectResponse(login_url, status.HTTP_303_SEE_OTHER)
    return response


@auth_router.get("/{provider}/callback", status_code=status.HTTP_200_OK)
async def sso_callback(
    service: UserServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    request: Request,
    code: str = Query(),
    state: str | None = Query(None),
    pkce_code_verifier: str | None = Cookie(None),
) -> BearerToken:
    callback = SSOCallback(
        code=code,
        url=str(request.url),
        state=state,
        pkce_code_verifier=pkce_code_verifier,
    )
    return await service.sso_callback(provider, callback)


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/me", status_code=status.HTTP_200_OK)
def me(user: UserDep) -> UserRead:
    return user


@user_router.patch("/me", status_code=status.HTTP_200_OK)
async def patch(
    service: UserServiceDep, user: UserDep, update: UserUpdate
) -> UserRead:
    return await service.update(user.id, update)


@user_router.delete("/me", status_code=status.HTTP_200_OK)
async def delete(service: UserServiceDep, user: UserDep) -> UserRead:
    return await service.delete(user.id)


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
