from typing import Annotated, Any

from fastapi import Depends, APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.db.schemas import PageParams, Page
from app.schemas import BackendOK
from app.sso.base import SSOBase
from app.sso.dependencies import get_sso
from app.sso.forms import SSOProviderOAuth2Form, SSOProviderAuthorize
from app.sso.schemas import SSOCallback
from app.sso_accounts.schemas import (
    URLResponse,
    SSOAccountRead,
    SSOAccountCreate,
)
from app.telegram.dependencies import bot, get_telegram_sso
from app.telegram.schemas import TelegramAuthData
from app.telegram.sso import TelegramSSO
from app.templating import templates
from app.users.constants import CALLBACK_WARNING
from app.users.dependencies import (
    UserServiceDep,
    UserDep,
    get_user_by_id,
    Requires,
)
from app.users.forms import AuthorizationForm
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


@sso_router.get(
    "/telegram/login",
    description="""
Redirects user to the Telegram login page.

Testing:
Telegram Redirect URI: `http://localhost:8000/api/v1/sso/telegram/callback`

Authorization URL: `http://localhost:8000/api/v1/sso/telegram/login?redirect_uri=http://localhost:8000/api/v1/sso/telegram/callback`
""",
    status_code=status.HTTP_303_SEE_OTHER,
)
async def telegram_login(
    provider: Annotated[TelegramSSO, Depends(get_telegram_sso)],
    params: Annotated[SSOProviderAuthorize, Depends()],
) -> Any:
    login_url = await provider.get_login_url(params.redirect_uri)
    if not params.redirect:
        return URLResponse(url=login_url)
    return RedirectResponse(
        url=login_url, status_code=status.HTTP_303_SEE_OTHER
    )


@sso_router.post("/telegram/token", status_code=status.HTTP_200_OK)
async def telegram_token(
    provider: Annotated[TelegramSSO, Depends(get_telegram_sso)],
    service: Annotated[UserServiceDep, Depends()],
    auth_data: TelegramAuthData,
) -> BearerToken:
    open_id = await provider.validate_auth_data(auth_data)
    account = SSOAccountCreate(
        **open_id.model_dump(exclude={"id"}),
        account_id=open_id.id,
    )
    return await service.authorize_sso(account)


@sso_router.get(
    "/telegram/callback",
    status_code=status.HTTP_200_OK,
    description=CALLBACK_WARNING,
)
async def telegram_callback(request: Request) -> Any:
    bot_me = await bot.me()
    print(request.url_for("telegram_view_data"))
    return templates.TemplateResponse(
        "telegram_login.html",
        {
            "request": request,
            "bot_username": bot_me.username,
            "redirect_uri": request.url_for("telegram_view_data"),
        },
    )


@sso_router.get(
    "/telegram/view",
    status_code=status.HTTP_200_OK,
    description=CALLBACK_WARNING,
)
def telegram_view_data(
    auth_data: Annotated[TelegramAuthData, Depends()],
) -> TelegramAuthData:
    return auth_data


@sso_router.post("/telegram/connect", status_code=status.HTTP_201_CREATED)
async def telegram_connect(
    service: UserServiceDep,
    provider: Annotated[TelegramSSO, Depends(get_telegram_sso)],
    user: UserDep,
    auth_data: Annotated[TelegramAuthData, Depends()],
) -> SSOAccountRead:
    open_id = await provider.validate_auth_data(auth_data)
    account = SSOAccountCreate(
        **open_id.model_dump(exclude={"id"}),
        account_id=open_id.id,
    )
    return await service.connect(user, account)


@sso_router.get(
    "/{provider}/login",
    description="""
    Redirects user to the provider's login page.

    Testing:
    Google Redirect URI: `http://localhost:8000/api/v1/sso/google/callback`
    Yandex Redirect URI: `http://localhost:8000/api/v1/sso/yandex/callback`
    """,
    status_code=status.HTTP_303_SEE_OTHER,
    tags=["SSO"],
)
async def sso_login(
    provider: Annotated[SSOBase, Depends(get_sso)],
    params: Annotated[SSOProviderAuthorize, Depends()],
) -> Any:
    login_url = await provider.get_login_url(
        redirect_uri=params.redirect_uri, state=params.state
    )
    if params.redirect:
        return provider.redirect(login_url)
    return URLResponse(url=login_url)


@sso_router.post(
    "/{provider}/token",
    description="Exchanges authorization code for token.",
    status_code=status.HTTP_200_OK,
    tags=["SSO"],
)
async def sso_token(
    service: UserServiceDep,
    provider: Annotated[SSOBase, Depends(get_sso)],
    form: Annotated[SSOProviderOAuth2Form, Depends()],
) -> BearerToken:
    callback = SSOCallback(
        code=form.code,
        redirect_uri=form.redirect_uri,
    )
    data = await service.get_data_from_provider(provider, callback)
    return await service.authorize_sso(data)


@sso_router.get(
    "/{provider}/callback",
    status_code=status.HTTP_200_OK,
    description=CALLBACK_WARNING,
    tags=["SSO"],
)
async def sso_callback(
    provider: Annotated[SSOBase, Depends(get_sso)],
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
    provider: Annotated[SSOBase, Depends(get_sso)],
    user: UserDep,
    form: Annotated[SSOProviderOAuth2Form, Depends()],
) -> SSOAccountRead:
    callback = SSOCallback(
        code=form.code,
        redirect_uri=form.redirect_uri,
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
    service: UserServiceDep, user: UserDep, via: NotifyVia = NotifyVia.email
) -> BackendOK:
    return await service.send_code(user, via)


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
