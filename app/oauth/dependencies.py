from enum import StrEnum, auto
from typing import Annotated, assert_never

from fastapi import Depends
from starlette import status
from starlette.responses import RedirectResponse

from app.config import settings
from app.oauth.exceptions import SSODisabled
from app.oauth.google import GoogleOAuth2
from app.oauth.interfaces import IOAuth2
from app.oauth.schemas import AuthorizationURL
from app.oauth.telegram import TelegramOAuth2
from app.oauth.yandex import YandexOAuth2
from app.telegram.dependencies import BotDep


def get_google_sso() -> IOAuth2:
    return GoogleOAuth2(
        settings.google.client_id,
        settings.google.client_secret,
    )


def get_yandex_sso() -> IOAuth2:
    return YandexOAuth2(
        settings.yandex.client_id,
        settings.yandex.client_secret,
    )


def get_telegram_sso(bot: BotDep) -> TelegramOAuth2:
    return TelegramOAuth2(bot, auth_expire=settings.telegram.auth_expire)


GoogleSSODep = Annotated[IOAuth2, Depends(get_google_sso)]
YandexSSODep = Annotated[IOAuth2, Depends(get_yandex_sso)]
TelegramSSODep = Annotated[IOAuth2, Depends(get_telegram_sso)]


class SSOName(StrEnum):
    google = auto()
    yandex = auto()
    telegram = auto()


def valid_sso(provider: SSOName) -> SSOName:
    match provider:
        case SSOName.google:
            is_enabled = settings.google.sso
        case SSOName.yandex:
            is_enabled = settings.yandex.sso
        case SSOName.telegram:
            is_enabled = settings.telegram.sso
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
