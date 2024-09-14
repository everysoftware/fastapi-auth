from typing import Annotated, Any, Literal

from aiogram.utils.deep_linking import create_start_link
from fastapi import Depends, APIRouter, Query, Form
from pydantic import AnyHttpUrl
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.config import settings
from app.db.schemas import PageParams, Page
from app.schemas import BackendOK
from app.sso.base import SSOProvider
from app.sso.dependencies import get_sso
from app.sso.exceptions import SSODisabled
from app.sso.schemas import SSOCallback, OpenID
from app.sso_accounts.schemas import (
    URLResponse,
    SSOAccountRead,
    SSOAccountCreate,
)
from app.telegram.bot import bot
from app.users.auth import AuthorizationForm
from app.users.constants import CALLBACK_URL_EXAMPLE
from app.users.dependencies import (
    UserServiceDep,
    UserDep,
    get_user_by_id,
    Requires,
)
from app.users.schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
    BearerToken,
    Role,
    NotifyVia,
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    service: UserServiceDep,
    user: UserCreate,
) -> UserRead:
    return await service.register(
        user.first_name, user.last_name, user.email, user.password
    )


@auth_router.post(
    "/token",
    description="""Grant types:
    **Password grant** requires username and password.
    **Refresh token grant** requires refresh token.
    """,
    status_code=status.HTTP_200_OK,
)
async def get_token(
    service: UserServiceDep,
    form: Annotated[AuthorizationForm, Depends()],
) -> BearerToken:
    return await service.authorize(form)


sso_router = APIRouter(prefix="/sso", tags=["SSO"])


@sso_router.get("/telegram/login", status_code=status.HTTP_303_SEE_OTHER)
async def telegram_login(user: UserDep, redirect: bool = True) -> Any:
    if not settings.auth.telegram_sso_enabled:
        raise SSODisabled()
    login_url = await create_start_link(bot, user.id)
    if not redirect:
        return URLResponse(url=login_url)
    return RedirectResponse(
        url=login_url, status_code=status.HTTP_303_SEE_OTHER
    )


@sso_router.post("/telegram/callback", status_code=status.HTTP_200_OK)
def telegram_callback(bot_code: str, open_id: OpenID) -> dict[str, Any]:
    return {"bot_code": bot_code, "open_id": open_id.model_dump()}


@sso_router.post("/telegram/connect", status_code=status.HTTP_200_OK)
async def telegram_connect(
    service: UserServiceDep, bot_code: str, open_id: OpenID
) -> SSOAccountRead:
    user = await service.get_one(bot_code)
    data = SSOAccountCreate(
        account_id=open_id.id, **open_id.model_dump(exclude={"id"})
    )
    return await service.connect(user, data)


@sso_router.get(
    "/{provider}/login",
    description="""Redirects user to the provider's login page.

    SSO flow:
    1. Frontend requests provider login URL (GET api.example.com/sso/{provider}/login) and redirects user to it.
    2. Provider redirects user back to the redirect URI with authorization code (e.g. GET example.com/sso-callback).
    3. Frontend sends the code to the backend to obtain token (POST api.example.com/sso/{provider}/token).
    4. Frontend uses the token to authenticate the user (e.g. GET api.example.com/users/me).
    """,
    status_code=status.HTTP_303_SEE_OTHER,
    tags=["SSO"],
)
async def sso_login(
    provider: Annotated[SSOProvider, Depends(get_sso)],
    redirect_uri: AnyHttpUrl = Query(
        openapi_examples={
            "Test example": {
                "summary": "",
                "value": CALLBACK_URL_EXAMPLE,
            }
        }
    ),
    state: str = Query(
        openapi_examples={
            "Test example": {"summary": "", "value": "test_state"}
        }
    ),
    redirect: bool = True,
) -> Any:
    login_url = await provider.get_login_url(
        redirect_uri=redirect_uri, state=state
    )
    if redirect:
        return provider.get_login_redirect(login_url)
    return URLResponse(url=login_url)


@sso_router.post(
    "/{provider}/token",
    description="Exchanges authorization code for token.",
    status_code=status.HTTP_200_OK,
    tags=["SSO"],
)
async def sso_token(
    service: UserServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    grant_type: Literal["authorization_code"] = Form(),
    code: str = Form(),
    redirect_uri: AnyHttpUrl = Form(examples=[CALLBACK_URL_EXAMPLE]),
) -> BearerToken:
    callback = SSOCallback(
        grant_type=grant_type, code=code, redirect_uri=redirect_uri
    )
    data = await service.get_data_from_provider(provider, callback)
    return await service.authorize_sso(data)


@sso_router.get(
    "/{provider}/callback",
    status_code=status.HTTP_200_OK,
    tags=["SSO"],
)
async def sso_callback(
    provider: Annotated[SSOProvider, Depends(get_sso)],
    request: Request,
    code: str,
    state: str,
    scope: str | None = None,
) -> dict[str, Any]:
    return {
        "url": str(request.url),
        "provider": provider.provider,
        "code": code,
        "scope": scope,
        "state": state,
    }


@sso_router.post("/{provider}/connect", status_code=status.HTTP_201_CREATED)
async def connect(
    service: UserServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    user: UserDep,
    grant_type: Literal["authorization_code"] = Form(),
    code: str = Form(),
    redirect_uri: AnyHttpUrl = Form(examples=[CALLBACK_URL_EXAMPLE]),
) -> SSOAccountRead:
    callback = SSOCallback(
        grant_type=grant_type, code=code, redirect_uri=redirect_uri
    )
    data = await service.get_data_from_provider(provider, callback)
    return await service.connect(user, data)


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(
    "/verify",
    dependencies=[Depends(Requires(is_verified=False))],
    status_code=status.HTTP_200_OK,
)
async def verify(
    service: UserServiceDep, user: UserDep, code: str
) -> UserRead:
    return await service.verify(user, code)


@user_router.get("/me", status_code=status.HTTP_200_OK)
def me(user: UserDep) -> UserRead:
    return user


@user_router.patch("/me", status_code=status.HTTP_200_OK)
async def patch(
    service: UserServiceDep, user: UserDep, update: UserUpdate
) -> UserRead:
    return await service.update(user, update)


@user_router.delete("/me", status_code=status.HTTP_200_OK)
async def delete(service: UserServiceDep, user: UserDep) -> UserRead:
    return await service.delete(user)


notify_router = APIRouter(prefix="/notify", tags=["Notifications"])


@notify_router.post("/code", status_code=status.HTTP_200_OK)
async def send_code(
    service: UserServiceDep, user: UserDep, via: NotifyVia = "email"
) -> BackendOK:
    return await service.send_code(user)


@notify_router.get("/code/verify", status_code=status.HTTP_200_OK)
async def verify_code(
    service: UserServiceDep,
    user: UserDep,
    code: str,
) -> BackendOK:
    return await service.validate_code(user, code)


admin_router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(Requires(is_superuser=True))],
)


@admin_router.get("/{user_id}")
def get_by_id(user: Annotated[UserRead, Depends(get_user_by_id)]) -> UserRead:
    return user


@admin_router.patch("/{user_id}")
async def update_by_id(
    service: UserServiceDep,
    user: Annotated[UserRead, Depends(get_user_by_id)],
    update: UserUpdate,
) -> UserRead:
    return await service.update(user, update)


@admin_router.delete("/{user_id}")
async def delete_by_id(
    service: UserServiceDep, user: Annotated[UserRead, Depends(get_user_by_id)]
) -> UserRead:
    return await service.delete(user)


@admin_router.get("/")
async def get_many(
    service: UserServiceDep, params: Annotated[PageParams, Depends()]
) -> Page[UserRead]:
    return await service.get_many(params)


@admin_router.post("/{user_id}/grant")
async def grant(
    service: UserServiceDep,
    user: Annotated[UserRead, Depends(get_user_by_id)],
    role: Role = Role.user,
) -> UserRead:
    return await service.grant(user, role)


user_router.include_router(admin_router)
