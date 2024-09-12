from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.db.types import ID
from app.users.auth import PasswordBearerAuth
from app.users.exceptions import NoPermission
from app.users.schemas import UserRead
from app.users.service import UserService

UserServiceDep = Annotated[UserService, Depends()]

password_scheme = PasswordBearerAuth(
    tokenUrl="auth/token", scheme_name="Password"
)
google_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="sso/google/login",
    tokenUrl="sso/google/token",
    refreshUrl="auth/token",
    scheme_name="GoogleOAuth",
)
yandex_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="sso/yandex/login",
    tokenUrl="sso/yandex/token",
    refreshUrl="auth/token",
    scheme_name="YandexOAuth",
)


def get_token(
    token: Annotated[str, Depends(password_scheme)],
    google_token: Annotated[str, Depends(google_scheme)],
    yandex_token: Annotated[str, Depends(yandex_scheme)],
) -> str:
    return token or google_token or yandex_token


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
