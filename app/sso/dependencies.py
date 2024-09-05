from typing import assert_never

from app.config import settings
from .base import SSOProvider
from .exceptions import SSODisabled
from .google import GoogleSSO
from .schemas import SSOName
from .yandex import YandexSSO


def get_sso(provider: SSOName) -> SSOProvider:
    match provider:
        case SSOName.google:
            if not settings.auth.google_sso_enabled:
                raise SSODisabled()
            sso_provider = GoogleSSO(
                settings.auth.google_client_id,
                settings.auth.google_client_secret,
                settings.auth.google_redirect_uri,
            )
        case SSOName.yandex:
            if not settings.auth.yandex_sso_enabled:
                raise SSODisabled()
            sso_provider = YandexSSO(
                settings.auth.yandex_client_id,
                settings.auth.yandex_client_secret,
                settings.auth.yandex_redirect_uri,
            )
        case _:
            assert_never(provider)

    return sso_provider
