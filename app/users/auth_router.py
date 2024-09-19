from typing import Annotated

from fastapi import Depends, APIRouter
from pydantic import EmailStr
from starlette import status

from app.schemas import BackendOK, backend_ok
from app.users.dependencies import (
    UserServiceDep,
)
from app.users.forms import AuthorizationForm
from app.users.schemas import (
    UserCreate,
    UserRead,
    BearerToken,
    NotifyVia,
    ResetPassword,
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    service: UserServiceDep,
    user: UserCreate,
) -> UserRead:
    return await service.register(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=user.password,
    )


@auth_router.post(
    "/token",
    description="""Grant types:
- **Password grant** requires username and password.
- **Refresh token grant** requires refresh token.
    """,
    status_code=status.HTTP_200_OK,
)
async def get_token(
    service: UserServiceDep,
    form: Annotated[AuthorizationForm, Depends()],
) -> BearerToken:
    return await service.authorize(form)


@auth_router.post(
    "/reset-password-request",
    status_code=status.HTTP_200_OK,
)
async def reset_password_request(
    service: UserServiceDep, email: EmailStr
) -> BackendOK:
    await service.send_code(via=NotifyVia.email, email=email)
    return backend_ok


@auth_router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    service: UserServiceDep, reset: ResetPassword
) -> BackendOK:
    await service.reset_password(reset)
    return backend_ok
