from typing import Annotated, NoReturn

from fastapi import HTTPException, Depends
from fastapi.security import APIKeyCookie, APIKeyHeader
from starlette import status

from app.database.types import ID
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


async def get_current_user(
    users: UserServiceDep,
    cookie_token: str = Depends(parse_cookies),
    header_token: str = Depends(parse_headers),
) -> UserRead:
    for token in cookie_token, header_token:
        try:
            return await users.validate(token)
        except InvalidToken as e:
            print(f"Invalid token: {e}")
    raise_unauthorized()


UserDep = Annotated[UserRead, Depends(get_current_user)]


async def get_user(users: UserServiceDep, current_user: UserDep, user_id: ID):
    # 1. User role: admin, user
    # 2. Permissions: tasks:read, tasks: update, tasks:delete...
    user = await users.get(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User does not exist")
    return user
