from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    OAuth2AuthorizationCodeBearer,
    APIKeyHeader,
    APIKeyCookie,
)

from app.db.types import ID
from app.users.auth import BackendAuth
from app.users.constants import TOKEN_HEADER_NAME, TOKEN_COOKIE_NAME
from app.users.exceptions import NoPermission
from app.users.schemas import UserRead
from app.users.service import UserService

UserServiceDep = Annotated[UserService, Depends()]
auth = BackendAuth(
    tokenUrl="auth/token", scheme_name="Password", auto_error=False
)
google_auth = OAuth2AuthorizationCodeBearer(
    authorizationUrl="sso/google/login",
    tokenUrl="sso/google/token",
    refreshUrl="auth/token",
    scheme_name="GoogleOAuth",
    auto_error=False,
)
yandex_auth = OAuth2AuthorizationCodeBearer(
    authorizationUrl="sso/yandex/login",
    tokenUrl="sso/yandex/token",
    refreshUrl="auth/token",
    scheme_name="YandexOAuth",
    auto_error=False,
)
header_auth = APIKeyHeader(
    name=TOKEN_HEADER_NAME,
    scheme_name="BearerHeader",
    auto_error=False,
)
cookie_auth = APIKeyCookie(
    name=TOKEN_COOKIE_NAME,
    scheme_name="BearerCookie",
    auto_error=False,
)


def get_token(
    token: Annotated[str, Depends(auth)],
    _google_token: Annotated[str | None, Depends(google_auth)],
    _yandex_token: Annotated[str | None, Depends(yandex_auth)],
    _header_token: Annotated[str | None, Depends(header_auth)],
    _cookie_auth: Annotated[str | None, Depends(cookie_auth)],
) -> str:
    return token


class GetCurrentUser:
    async def __call__(
        self,
        users: UserServiceDep,
        token: Annotated[str, Depends(get_token)],
    ) -> UserRead:
        return await users.validate_token(token)


get_user = GetCurrentUser()
UserDep = Annotated[UserRead, Depends(get_user)]


class Requires:
    def __init__(
        self,
        is_superuser: bool | None = None,
        has_password: bool | None = None,
        is_verified: bool | None = None,
        is_active: bool | None = None,
    ):
        self.is_superuser = is_superuser
        self.has_password = has_password
        self.is_verified = is_verified
        self.is_active = is_active

    async def __call__(
        self,
        users: UserServiceDep,
        user: UserDep,
    ) -> UserRead:
        if (
            self.is_superuser is not None
            and user.is_superuser != self.is_superuser
        ):
            raise NoPermission()
        if (
            self.has_password is not None
            and user.has_password != self.has_password
        ):
            raise NoPermission()
        if (
            self.is_verified is not None
            and user.is_verified != self.is_verified
        ):
            raise NoPermission()
        if self.is_active is not None and user.is_active != self.is_active:
            raise NoPermission()
        return user


async def get_user_by_id(users: UserServiceDep, user_id: ID) -> UserRead:
    return await users.get_one(user_id)
