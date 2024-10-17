from typing import Annotated

from fastapi import Depends, APIRouter
from pydantic import EmailStr
from starlette import status
from starlette.responses import JSONResponse

from app.schemas import BackendOK, backend_ok
from app.users.constants import TOKEN_COOKIE_NAME
from app.users.dependencies import (
    UserServiceDep,
)
from app.users.auth import AuthorizationForm
from app.users.schemas import (
    UserCreate,
    UserRead,
    NotifyVia,
    ResetPassword,
    BearerToken,
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
    response_model=BearerToken,
)
async def get_token(
    service: UserServiceDep,
    form: Annotated[AuthorizationForm, Depends()],
) -> JSONResponse:
    token = await service.authorize(form)
    response = JSONResponse(content=token.model_dump(mode="json"))
    response.set_cookie(
        key=TOKEN_COOKIE_NAME,
        value=token.access_token,
        httponly=True,
        max_age=token.expires_in,
    )
    return response


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
