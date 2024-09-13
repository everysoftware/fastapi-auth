from typing import Annotated

from fastapi import Depends

from app.db.types import ID
from app.sso_accounts.schemas import SSOAccountRead

from app.sso_accounts.service import SSOAccountService

SSOAccountServiceDep = Annotated[SSOAccountService, Depends()]


async def get_account(
    service: SSOAccountServiceDep, account_id: ID
) -> SSOAccountRead:
    return await service.get_one(account_id)
