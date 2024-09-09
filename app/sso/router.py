from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Form
from pydantic import AnyHttpUrl
from starlette import status

from app.db.schemas import PageParams, Page
from app.oidc.base import SSOProvider
from app.oidc.schemas import SSOCallback
from app.sso.dependencies import get_sso
from app.sso.schemas import SSOAccountRead
from app.users.constants import CALLBACK_URL_EXAMPLE
from app.users.dependencies import UserServiceDep, UserDep

router = APIRouter(prefix="/sso-accounts", tags=["SSO Accounts"])


@router.post("/{provider}", status_code=status.HTTP_201_CREATED)
async def sso_connect(
    service: UserServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    user: UserDep,
    grant_type: Literal["authorization_code"] = Form(),
    code: str = Form(),
    redirect_uri: AnyHttpUrl = Form(examples=[CALLBACK_URL_EXAMPLE]),
) -> SSOAccountRead:
    callback = SSOCallback(
        grant_type=grant_type, code=code, redirect_uri=redirect_uri
    )
    return await service.sso_connect(user, provider, callback)


@router.get("/", status_code=status.HTTP_200_OK)
async def sso_paginate(
    service: UserServiceDep,
    user: UserDep,
    params: Annotated[PageParams, Depends()],
) -> Page[SSOAccountRead]:
    return await service.paginate_sso_accounts(user, params)
