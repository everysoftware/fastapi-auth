from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.db.types import ID
from app.dependencies import UOWDep
from app.users.auth import PasswordBearerAuth
from app.users.exceptions import (
    SuperuserRightsRequired,
    PasswordSettingRequired,
    VerificationRequired,
    UserDisabled,
)
from app.users.schemas import UserRead
from app.users.service import UserService


def get_user_service(
    uow: UOWDep,
) -> UserService:
    return UserService(uow)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]

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


class GetCurrentUser:
    def __init__(
        self,
        requires_superuser: bool = False,
        requires_password: bool = False,
        requires_verified: bool = False,
        requires_active: bool = True,
    ):
        self.requires_superuser = requires_superuser
        self.requires_password = requires_password
        self.requires_verified = requires_verified
        self.requires_active = requires_active

    async def __call__(
        self,
        users: UserServiceDep,
        token: Annotated[str, Depends(password_scheme)],
        _: Annotated[str, Depends(google_scheme)],
        __: Annotated[str, Depends(yandex_scheme)],
    ) -> UserRead:
        user = await users.validate_token(token)
        if self.requires_superuser and not user.is_superuser:
            if not user.is_superuser:
                raise SuperuserRightsRequired()
        if self.requires_password and not user.has_password:
            raise PasswordSettingRequired()
        if self.requires_verified and not user.is_verified:
            raise VerificationRequired()
        if self.requires_active and not user.is_active:
            raise UserDisabled()
        return user


UserDep = Annotated[UserRead, Depends(GetCurrentUser())]
SuperuserDep = Annotated[
    UserRead, Depends(GetCurrentUser(requires_superuser=True))
]
PasswordUserDep = Annotated[
    UserRead, Depends(GetCurrentUser(requires_password=True))
]


async def get_user(users: UserServiceDep, user_id: ID) -> UserRead:
    return await users.get_one(user_id)
