from typing import assert_never

from app.config import settings
from app.oidc.base import SSOProvider
from app.oidc.google import GoogleSSO
from app.oidc.schemas import SSOName
from app.oidc.yandex import YandexSSO
from app.sso.exceptions import SSODisabled


def get_sso(provider: SSOName) -> SSOProvider:
    match provider:
        case SSOName.google:
            if not settings.auth.google_sso_enabled:
                raise SSODisabled()
            return GoogleSSO(
                settings.auth.google_client_id,
                settings.auth.google_client_secret,
                settings.auth.google_redirect_uri,
            )
        case SSOName.yandex:
            if not settings.auth.yandex_sso_enabled:
                raise SSODisabled()
            return YandexSSO(
                settings.auth.yandex_client_id,
                settings.auth.yandex_client_secret,
                settings.auth.yandex_redirect_uri,
            )
        case _:
            assert_never(provider)
