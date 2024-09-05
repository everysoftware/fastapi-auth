from typing import Annotated

from fastapi import APIRouter, Depends, Query, Cookie
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.sso.providers.base import SSOProvider
from app.sso.providers.schemas import SSOCallback
from app.sso.dependencies import SSOServiceDep, get_sso
from app.users.schemas import BearerToken

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/{provider}", status_code=status.HTTP_303_SEE_OTHER)
async def sso_login(
    service: SSOServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    redirect_uri: str | None = Query(None),
) -> RedirectResponse:
    login_url = await service.sso_login(provider, redirect_uri)
    response = RedirectResponse(login_url, status.HTTP_303_SEE_OTHER)
    return response


@router.get("/{provider}/callback", status_code=status.HTTP_200_OK)
async def sso_callback(
    service: SSOServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    request: Request,
    code: str = Query(),
    state: str | None = Query(None),
    pkce_code_verifier: str | None = Cookie(None),
) -> BearerToken:
    callback = SSOCallback(
        code=code,
        url=str(request.url),
        state=state,
        pkce_code_verifier=pkce_code_verifier,
    )
    return await service.sso_callback(provider, callback)
