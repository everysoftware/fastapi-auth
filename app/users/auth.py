from typing import Annotated, assert_never, NoReturn

from fastapi import Form
from fastapi.security import (
    OAuth2PasswordBearer as FastAPIOAuth2PasswordBearer,
    OAuth2PasswordRequestForm as FastAPIOAuth2PasswordRequestForm,
)
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request

from app.exceptions import ValidationError
from app.users.constants import TOKEN_HEADER_NAME, TOKEN_COOKIE_NAME
from app.users.exceptions import NoTokenProvided
from app.users.schemas import GrantType


def raise_form_exc(msg: str) -> NoReturn:
    raise ValidationError(
        [
            {
                "loc": "form",
                "msg": msg,
            }
        ]
    )


class AuthorizationForm(FastAPIOAuth2PasswordRequestForm):
    def __init__(
        self,
        *,
        grant_type: Annotated[
            GrantType,
            Form(),
        ],
        # Password
        username: Annotated[
            str | None,
            Form(
                examples=["user@example.com"],
            ),
        ] = None,
        password: Annotated[
            str | None,
            Form(examples=["password"]),
        ] = None,
        # Refresh token
        refresh_token: Annotated[str | None, Form()] = None,
    ):
        match grant_type:
            case GrantType.password:
                if not username or not password:
                    raise_form_exc("Username and password are required")
            case GrantType.refresh_token:
                if not refresh_token:
                    raise_form_exc("Refresh token is required")
            case _:
                assert_never(grant_type)

        self.refresh_token = refresh_token

        super().__init__(
            grant_type=grant_type,
            username=username,  # type: ignore[arg-type]
            password=password,  # type: ignore[arg-type]
            scope="",
            client_id="",
            client_secret="",
        )


def get_from_cookies(request: Request) -> str | None:
    return request.cookies.get(TOKEN_COOKIE_NAME)


def get_from_headers(request: Request) -> str | None:
    authorization = request.headers.get(TOKEN_HEADER_NAME)
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        return None
    return param


class PasswordBearerAuth(FastAPIOAuth2PasswordBearer):
    parsers = [get_from_cookies, get_from_headers]

    async def __call__(self, request: Request) -> str | None:
        for parser in self.parsers:
            token = parser(request)
            if token:
                return token
        if self.auto_error:
            raise NoTokenProvided()
        else:
            return None
