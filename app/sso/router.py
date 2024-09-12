from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Form
from pydantic import AnyHttpUrl
from starlette import status

from app.db.schemas import PageParams, Page
from app.oidc.base import SSOProvider
from app.oidc.schemas import SSOCallback
from app.sso.dependencies import get_sso, SSOAccountServiceDep, get_account
from app.sso.schemas import SSOAccountRead
from app.users.constants import CALLBACK_URL_EXAMPLE
from app.users.dependencies import UserDep, Requires

router = APIRouter(prefix="/sso-accounts", tags=["SSO Accounts"])


@router.post("/{provider}", status_code=status.HTTP_201_CREATED)
async def connect(
    service: SSOAccountServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    user: UserDep,
    grant_type: Literal["authorization_code"] = Form(),
    code: str = Form(),
    redirect_uri: AnyHttpUrl = Form(examples=[CALLBACK_URL_EXAMPLE]),
) -> SSOAccountRead:
    callback = SSOCallback(
        grant_type=grant_type, code=code, redirect_uri=redirect_uri
    )
    return await service.connect(user, provider, callback)


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
