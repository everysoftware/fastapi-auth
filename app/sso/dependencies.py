from typing import Annotated, assert_never

from fastapi import Depends

from app.config import settings
from app.dependencies import UOWDep
from app.sso.exceptions import SSODisabled
from app.sso.providers.base import SSOProvider
from app.sso.providers.google import GoogleSSO
from app.sso.providers.schemas import SSOName
from app.sso.providers.yandex import YandexSSO
from app.sso.service import SSOService
from app.users.dependencies import UserServiceDep


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


def get_sso_service(uow: UOWDep, users: UserServiceDep) -> SSOService:
    return SSOService(uow, users=users)


SSOServiceDep = Annotated[SSOService, Depends(get_sso_service)]
