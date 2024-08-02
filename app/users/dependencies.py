from typing import Annotated

from fastapi import HTTPException, Depends, Header
from starlette import status

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


async def get_current_user(
    users: UserServiceDep, access_token: str = Header()
) -> UserRead:
    try:
        user = await users.validate(access_token)
    except InvalidToken as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )
    return user


UserDep = Annotated[UserRead, Depends(get_current_user)]
