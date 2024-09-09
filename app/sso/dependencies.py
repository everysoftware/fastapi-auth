from typing import assert_never, Annotated

from fastapi import Depends

from app.config import settings
from app.db.types import ID
from app.dependencies import UOWDep
from app.oidc.base import SSOProvider
from app.oidc.google import GoogleSSO
from app.oidc.schemas import SSOName
from app.oidc.yandex import YandexSSO
from app.sso.exceptions import SSODisabled
from app.sso.schemas import SSOAccountRead
from app.sso.service import SSOAccountService
from app.users.dependencies import UserServiceDep


def get_sso(provider: SSOName) -> SSOProvider:
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


def get_sso_account_service(
    uow: UOWDep, users: UserServiceDep
) -> SSOAccountService:
    return SSOAccountService(uow, users)


SSOAccountServiceDep = Annotated[
    SSOAccountService, Depends(get_sso_account_service)
]


async def get_account(
    service: SSOAccountServiceDep, account_id: ID
) -> SSOAccountRead:
    return await service.get_one(account_id)
