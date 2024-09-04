from typing import Mapping

from fastapi_sso.sso.base import SSOBase
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.yandex import YandexSSO

from app.config import settings


class Provider(SSOBase):
    pass


class GoogleProvider(Provider, GoogleSSO):
    pass


class YandexProvider(Provider, YandexSSO):
    pass


class OIDC:
    providers: Mapping[str, Provider]

    def __init__(self, **providers: Provider):
        self.providers = providers

    def get_provider(self, name: str) -> Provider:
        return self.providers[name]


def get_oidc() -> OIDC:
    google = GoogleProvider(
        settings.auth.google_client_id,
        settings.auth.google_client_secret,
        settings.auth.google_redirect_uri,
    )
    yandex = YandexProvider(
        settings.auth.yandex_client_id,
        settings.auth.yandex_client_secret,
        settings.auth.yandex_redirect_uri,
    )
    return OIDC(google=google, yandex=yandex)
