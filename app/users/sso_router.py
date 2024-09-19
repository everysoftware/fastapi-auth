from typing import Annotated, Any

from fastapi import APIRouter, Depends
from starlette import status
from starlette.requests import Request

from app.sso.dependencies import valid_sso, redirect_sso
from app.sso.forms import SSOLoginParams, SSOCallbackForm
from app.sso.schemas import SSOName, SSOCallback
from app.sso.telegram import TelegramAuthData
from app.sso_accounts.schemas import SSOAccountRead
from app.templating import templates
from app.users.constants import CALLBACK_WARNING
from app.users.dependencies import UserServiceDep, UserDep
from app.users.schemas import BearerToken

router = APIRouter(prefix="/sso", tags=["SSO"])


@router.get(
    "/{provider}/login",
    description="""
Redirects user to the provider's login page.

## How to test

Google Redirect URI: `http://localhost:8000/api/v1/sso/google/callback`

Yandex Redirect URI: `http://localhost:8000/api/v1/sso/yandex/callback`

Telegram Redirect URI: `http://localhost:8000/api/v1/sso/telegram/callback`

Telegram Authorization URL:
`http://localhost:8000/api/v1/sso/telegram/login?redirect_uri=http://localhost:8000/api/v1/sso/telegram/callback`
""",
    status_code=status.HTTP_303_SEE_OTHER,
    tags=["SSO"],
)
async def sso_login(
    service: UserServiceDep,
    provider: Annotated[SSOName, Depends(valid_sso)],
    params: Annotated[SSOLoginParams, Depends()],
) -> Any:
    url = await service.get_login_url(
        provider, str(params.redirect_uri), params.state
    )
    return redirect_sso(url, params.redirect)


@router.post(
    "/telegram/token",
    description="""
Telegram does not support the classic OAuth2 Authorization Code flow.
It passes user data to the redirect page in a fragment that is only accessible in the browser.""",
    status_code=status.HTTP_200_OK,
)
async def telegram_token(
    service: UserServiceDep,
    auth_data: TelegramAuthData,
) -> BearerToken:
    data = await service.sso_callback(SSOName.telegram, auth_data)
    return await service.sso_authorize(data)


@router.get(
    "/telegram/callback",
    status_code=status.HTTP_200_OK,
    description=CALLBACK_WARNING,
)
async def telegram_callback(
    service: UserServiceDep,
    request: Request,
) -> Any:
    bot_me = await service.bot.me()
    return templates.TemplateResponse(
        "telegram_login.html",
        {
            "request": request,
            "bot_username": bot_me.username,
            "redirect_uri": request.url_for("telegram_view_data"),
        },
    )


@router.get(
    "/telegram/view",
    status_code=status.HTTP_200_OK,
    description=CALLBACK_WARNING,
)
def telegram_view_data(
    auth_data: Annotated[TelegramAuthData, Depends()],
) -> TelegramAuthData:
    return auth_data


@router.post("/telegram/connect", status_code=status.HTTP_201_CREATED)
async def telegram_connect(
    service: UserServiceDep,
    user: UserDep,
    auth_data: TelegramAuthData,
) -> SSOAccountRead:
    data = await service.sso_callback(SSOName.telegram, auth_data)
    return await service.sso_connect(user, data)


@router.post(
    "/{provider}/token",
    description="Exchanges authorization code for token.",
    status_code=status.HTTP_200_OK,
    tags=["SSO"],
)
async def sso_token(
    service: UserServiceDep,
    provider: Annotated[SSOName, Depends(valid_sso)],
    form: Annotated[SSOCallbackForm, Depends()],
) -> BearerToken:
    callback = SSOCallback(
        code=form.code,
        redirect_uri=form.redirect_uri,
    )
    data = await service.sso_callback(provider, callback)
    return await service.sso_authorize(data)


@router.get(
    "/{provider}/callback",
    status_code=status.HTTP_200_OK,
    description=CALLBACK_WARNING,
    tags=["SSO"],
)
async def sso_callback(
    provider: Annotated[SSOName, Depends(valid_sso)],
    request: Request,
    code: str,
    state: str,
    scope: str | None = None,
) -> dict[str, Any]:
    return {
        "url": str(request.url),
        "provider": provider,
        "code": code,
        "scope": scope,
        "state": state,
    }


@router.post("/{provider}/connect", status_code=status.HTTP_201_CREATED)
async def connect(
    service: UserServiceDep,
    provider: Annotated[SSOName, Depends(valid_sso)],
    user: UserDep,
    form: Annotated[SSOCallbackForm, Depends()],
) -> SSOAccountRead:
    callback = SSOCallback(
        code=form.code,
        redirect_uri=form.redirect_uri,
    )
    data = await service.sso_callback(provider, callback)
    return await service.sso_connect(user, data)
