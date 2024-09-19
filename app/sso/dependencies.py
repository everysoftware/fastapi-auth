from typing import Annotated, assert_never

from fastapi import Depends
from starlette import status
from starlette.responses import RedirectResponse

from app.config import settings
from app.sso.exceptions import SSODisabled
from app.sso.google import GoogleSSO
from app.sso.interfaces import ISSO
from app.sso.schemas import SSOName, AuthorizationURL
from app.sso.telegram import TelegramSSO
from app.sso.yandex import YandexSSO
from app.telegram.dependencies import BotDep


def get_google_sso() -> ISSO:
    return GoogleSSO(
        settings.auth.google_client_id,
        settings.auth.google_client_secret,
    )


def get_yandex_sso() -> ISSO:
    return YandexSSO(
        settings.auth.yandex_client_id,
        settings.auth.yandex_client_secret,
    )


def get_telegram_sso(bot: BotDep) -> TelegramSSO:
    if not settings.auth.telegram_sso_enabled:
        raise SSODisabled()
    return TelegramSSO(bot)


GoogleSSODep = Annotated[ISSO, Depends(get_google_sso)]
YandexSSODep = Annotated[ISSO, Depends(get_yandex_sso)]
TelegramSSODep = Annotated[ISSO, Depends(get_telegram_sso)]


def valid_sso(provider: SSOName) -> SSOName:
    match provider:
        case SSOName.google:
            is_enabled = settings.auth.google_sso_enabled
        case SSOName.yandex:
            is_enabled = settings.auth.yandex_sso_enabled
        case SSOName.telegram:
            is_enabled = settings.auth.telegram_sso_enabled
        case _:
            assert_never(provider)
    if not is_enabled:
        raise SSODisabled()
    return provider


def redirect_sso(
    url: str, redirect: bool = True
) -> RedirectResponse | AuthorizationURL:
    if not redirect:
        return AuthorizationURL(url=url)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
