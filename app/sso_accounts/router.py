from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.db.schemas import PageParams, Page
from app.sso_accounts.dependencies import SSOAccountServiceDep, get_account
from app.sso_accounts.schemas import SSOAccountRead
from app.users.dependencies import UserDep, Requires

router = APIRouter(prefix="/sso/accounts", tags=["SSO"])


@router.get(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
)
async def get(
    account: Annotated[SSOAccountRead, Depends(get_account)],
) -> SSOAccountRead:
    return account


@router.delete(
    "/{account_id}",
    dependencies=[Depends(Requires(has_password=True))],
    status_code=status.HTTP_200_OK,
)
async def delete(
    service: SSOAccountServiceDep,
    account: Annotated[SSOAccountRead, Depends(get_account)],
) -> SSOAccountRead:
    return await service.delete(account)


@router.get("/", status_code=status.HTTP_200_OK)
async def paginate(
    service: SSOAccountServiceDep,
    user: UserDep,
    params: Annotated[PageParams, Depends()],
) -> Page[SSOAccountRead]:
    return await service.paginate(user, params)
