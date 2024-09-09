from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.db.types import ID
from app.dependencies import UOWDep
from app.logging import logger
from app.users.auth import PasswordBearerAuth
from app.users.exceptions import SuperuserRightsRequired
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
    authorizationUrl="auth/google/login",
    tokenUrl="auth/google/token",
    refreshUrl="auth/token",
    scheme_name="GoogleOAuth",
)
yandex_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="auth/yandex/login",
    tokenUrl="auth/yandex/token",
    refreshUrl="auth/token",
    scheme_name="YandexOAuth",
)


class GetCurrentUser:
    is_superuser: bool

    def __init__(self, is_superuser: bool = False):
        self.is_superuser = is_superuser

    async def __call__(
        self,
        users: UserServiceDep,
        token: Annotated[str, Depends(password_scheme)],
        _: Annotated[str, Depends(google_scheme)],
        __: Annotated[str, Depends(yandex_scheme)],
    ) -> UserRead:
        logger.info("Obtained token: {token}", token=token)
        user = await users.validate_token(token)
        logger.info("Obtained user: {user}", user=user.model_dump())
        if self.is_superuser and not user.is_superuser:
            if not user.is_superuser:
                raise SuperuserRightsRequired()
        return user


UserDep = Annotated[UserRead, Depends(GetCurrentUser())]
SuperuserDep = Annotated[UserRead, Depends(GetCurrentUser(is_superuser=True))]


async def get_user(users: UserServiceDep, user_id: ID) -> UserRead:
    return await users.get_one(user_id)
