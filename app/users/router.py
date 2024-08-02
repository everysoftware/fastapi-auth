from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.users.dependencies import (
    get_user_create,
    UserServiceDep,
    UserDep,
)
from app.users.schemas import UserCreate, UserRead, UserUpdate, TokenInfo

router = APIRouter()

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    auth: UserServiceDep,
    user: Annotated[UserCreate, Depends(get_user_create)],
) -> UserRead:
    return await auth.register(user)


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    users: UserServiceDep,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenInfo:
    token_info = await users.login(form.username, form.password)
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return token_info


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/me", status_code=status.HTTP_200_OK)
async def me(user: UserDep) -> UserRead:
    return user


@user_router.put("/me", status_code=status.HTTP_200_OK)
async def put(
    users: UserServiceDep, user: UserDep, update: UserUpdate
) -> UserRead:
    return await users.update(user.id, update)


@user_router.delete("/me", status_code=status.HTTP_200_OK)
async def delete(users: UserServiceDep, user: UserDep) -> UserRead:
    return await users.delete(user.id)
