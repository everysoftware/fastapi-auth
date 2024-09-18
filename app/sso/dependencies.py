from typing import assert_never

from app.config import settings
from app.sso.base import SSOBase
from app.sso.exceptions import SSODisabled
from app.sso.google import GoogleSSO
from app.sso.schemas import SSOName
from app.sso.yandex import YandexSSO


def get_sso(provider: SSOName) -> SSOBase:
    match provider:
        case SSOName.google:
            if not settings.auth.google_sso_enabled:
                raise SSODisabled()
            return GoogleSSO(
                settings.auth.google_client_id,
                settings.auth.google_client_secret,
            )
        case SSOName.yandex:
            if not settings.auth.yandex_sso_enabled:
                raise SSODisabled()
            return YandexSSO(
                settings.auth.yandex_client_id,
                settings.auth.yandex_client_secret,
            )
        case _:
            assert_never(provider)
