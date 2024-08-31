from typing import Annotated

from fastapi import Depends

from app.db.types import ID
from app.dependencies import UOWDep
from app.logging import logger
from app.users.exceptions import SuperuserRightsRequired, UserNotFound
from app.users.oauth2 import CustomOAuth2PasswordBearer
from app.users.schemas import UserRead
from app.users.service import UserService


def get_user_service(
    uow: UOWDep,
) -> UserService:
    return UserService(uow)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]

oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="auth/token")


class GetCurrentUser:
    is_superuser: bool

    def __init__(self, is_superuser: bool = False):
        self.is_superuser = is_superuser

    async def __call__(
        self,
        users: UserServiceDep,
        token: Annotated[str, Depends(oauth2_scheme)],
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
    user = await users.get(user_id)
    if user is None:
        raise UserNotFound()
    return user
