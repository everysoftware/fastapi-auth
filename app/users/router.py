from typing import Annotated, Any, Literal

from fastapi import Depends, APIRouter, Query, Form
from pydantic import AnyHttpUrl
from starlette import status
from starlette.requests import Request

from app.db.schemas import PageParams, Page
from app.oidc.base import SSOProvider
from app.oidc.schemas import SSOCallback
from app.sso.dependencies import get_sso
from app.sso.schemas import URLResponse
from app.users.auth import AuthorizationForm
from app.users.constants import CALLBACK_URL_EXAMPLE
from app.users.dependencies import (
    UserServiceDep,
    UserDep,
    get_user,
    GetCurrentUser,
)
from app.users.schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
    BearerToken,
    Role,
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    service: UserServiceDep,
    user: UserCreate,
) -> UserRead:
    return await service.register(user.email, user.password)


@auth_router.post(
    "/token",
    description="""Grant types:
    **Password grant** requires username and password.
    **Refresh token grant** requires refresh token.
    """,
    status_code=status.HTTP_200_OK,
)
async def get_token(
    service: UserServiceDep,
    form: Annotated[AuthorizationForm, Depends()],
) -> BearerToken:
    return await service.authorize(form)


sso_router = APIRouter(prefix="/sso", tags=["SSO"])


@sso_router.get(
    "/{provider}/login",
    description="""Redirects user to the provider's login page.

    SSO flow:
    1. Frontend requests provider login URL (GET api.example.com/sso/{provider}/login) and redirects user to it.
    2. Provider redirects user back to the redirect URI with authorization code (e.g. GET example.com/sso-callback).
    3. Frontend sends the code to the backend to obtain token (POST api.example.com/sso/{provider}/token).
    4. Frontend uses the token to authenticate the user (e.g. GET api.example.com/users/me).
    """,
    status_code=status.HTTP_303_SEE_OTHER,
    tags=["SSO"],
)
async def sso_login(
    service: UserServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    redirect_uri: str = Query(
        openapi_examples={
            "Test example": {
                "summary": "",
                "value": CALLBACK_URL_EXAMPLE,
            }
        }
    ),
    state: str = Query(
        openapi_examples={
            "Test example": {"summary": "", "value": "test_state"}
        }
    ),
    redirect: bool = True,
) -> Any:
    login_url = await service.get_consent_url(
        provider,
        redirect_uri,
        state,
    )
    if redirect:
        return provider.get_login_redirect(login_url)
    return URLResponse(url=login_url)


@sso_router.post(
    "/{provider}/token",
    description="Exchanges authorization code for token.",
    status_code=status.HTTP_200_OK,
    tags=["SSO"],
)
async def sso_token(
    service: UserServiceDep,
    provider: Annotated[SSOProvider, Depends(get_sso)],
    grant_type: Literal["authorization_code"] = Form(),
    code: str = Form(),
    redirect_uri: AnyHttpUrl = Form(examples=[CALLBACK_URL_EXAMPLE]),
) -> BearerToken:
    callback = SSOCallback(
        grant_type=grant_type, code=code, redirect_uri=redirect_uri
    )
    return await service.sso_token(provider, callback)


@sso_router.get(
    "/{provider}/callback",
    status_code=status.HTTP_200_OK,
    tags=["SSO"],
)
async def sso_callback(
    provider: Annotated[SSOProvider, Depends(get_sso)],
    request: Request,
    code: str,
    state: str,
    scope: str | None = None,
) -> dict[str, Any]:
    return {
        "url": str(request.url),
        "provider": provider.provider,
        "code": code,
        "scope": scope,
        "state": state,
    }


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/me", status_code=status.HTTP_200_OK)
def me(user: UserDep) -> UserRead:
    return user


@user_router.patch("/me", status_code=status.HTTP_200_OK)
async def patch(
    service: UserServiceDep, user: UserDep, update: UserUpdate
) -> UserRead:
    return await service.update(user.id, update)


@user_router.delete("/me", status_code=status.HTTP_200_OK)
async def delete(service: UserServiceDep, user: UserDep) -> UserRead:
    return await service.delete(user.id)


su_router = APIRouter(
    tags=["Admin"], dependencies=[Depends(GetCurrentUser(is_superuser=True))]
)


@su_router.get("/{user_id}")
def get_by_id(user: Annotated[UserRead, Depends(get_user)]) -> UserRead:
    return user


@su_router.patch("/{user_id}")
async def update_by_id(
    service: UserServiceDep,
    user: Annotated[UserRead, Depends(get_user)],
    update: UserUpdate,
) -> UserRead:
    return await service.update(user.id, update)


@su_router.delete("/{user_id}")
async def delete_by_id(
    service: UserServiceDep, user: Annotated[UserRead, Depends(get_user)]
) -> UserRead:
    return await service.delete(user.id)


@su_router.get("/")
async def get_many(
    service: UserServiceDep, params: Annotated[PageParams, Depends()]
) -> Page[UserRead]:
    return await service.get_many(params)


@su_router.post("/{user_id}/grant")
async def grant(
    service: UserServiceDep,
    user: Annotated[UserRead, Depends(get_user)],
    role: Role = Role.user,
) -> UserRead:
    return await service.grant(user.id, role)


user_router.include_router(su_router)
