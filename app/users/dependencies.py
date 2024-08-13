from typing import Annotated, NoReturn

from fastapi import HTTPException, Depends
from fastapi.security import APIKeyCookie, APIKeyHeader
from starlette import status

from app.db.types import ID
from app.dependencies import UOWDep
from app.users.exceptions import InvalidToken
from app.users.schemas import UserCreate, UserRead
from app.users.service import UserService


def get_user_service(
    uow: UOWDep,
) -> UserService:
    return UserService(uow)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_user_create(
    users: UserServiceDep, creation: UserCreate
) -> UserCreate:
    user = await users.get_by_email(creation.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email `{creation.email}` already exists",
        )
    return creation


cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)
header_scheme = APIKeyHeader(name="Authentication", auto_error=False)


def raise_unauthorized() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )


async def parse_cookies(token: str = Depends(cookie_scheme)) -> str | None:
    return token


async def parse_headers(token: str = Depends(header_scheme)) -> str | None:
    if not token:
        return None
    header_lst = token.split()
    if len(header_lst) != 2:
        return None
    schema, token = header_lst
    if schema.lower() != "bearer":
        return None
    return token


class GetCurrentUser:
    is_superuser: bool

    def __init__(self, is_superuser: bool = False):
        self.is_superuser = is_superuser

    async def __call__(
        self,
        users: UserServiceDep,
        cookie_token: str = Depends(parse_cookies),
        header_token: str = Depends(parse_headers),
    ) -> UserRead:
        user = None
        for token in cookie_token, header_token:
            try:
                user = await users.validate(token)
            except InvalidToken as e:
                print(f"Invalid token error: {e}")
        if user is None:
            raise_unauthorized()
        if self.is_superuser and not user.is_superuser:
            if not user.is_superuser:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, "Not enough rights"
                )
        return user


UserDep = Annotated[UserRead, Depends(GetCurrentUser())]
SuperuserDep = Annotated[UserRead, Depends(GetCurrentUser(is_superuser=True))]


async def get_user(users: UserServiceDep, user_id: ID) -> UserRead:
    user = await users.get(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User does not exist")
    return user
