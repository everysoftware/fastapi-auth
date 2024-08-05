from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.settings import settings
from app.users.dependencies import (
    get_user_create,
    UserServiceDep,
    UserDep,
)
from app.users.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter()

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    auth: UserServiceDep,
    user: Annotated[UserCreate, Depends(get_user_create)],
) -> UserRead:
    return await auth.register(user)


@auth_router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(
    users: UserServiceDep,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Response:
    token_info = await users.login(form.username, form.password)
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.set_cookie(
        key="access_token",
        value=token_info.access_token,
        httponly=True,
        secure=True,
        max_age=settings.jwt_access_token_expire * 60,
    )
    return response


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    # Not always works
    # response.delete_cookie(key="access_token")
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=True,
        max_age=0,
    )
    return response


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/me", status_code=status.HTTP_200_OK)
async def me(user: UserDep) -> UserRead:
    return user


@user_router.patch("/me", status_code=status.HTTP_200_OK)
async def patch(
    users: UserServiceDep, user: UserDep, update: UserUpdate
) -> UserRead:
    return await users.update(user.id, update)


@user_router.delete("/me", status_code=status.HTTP_200_OK)
async def delete(users: UserServiceDep, user: UserDep) -> UserRead:
    return await users.delete(user.id)
