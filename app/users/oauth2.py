from typing import Annotated, assert_never

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


class AuthorizationForm(FastAPIOAuth2PasswordRequestForm):
    def __init__(
        self,
        *,
        grant_type: Annotated[
            GrantType,
            Form(pattern="password|refresh_token"),
        ],
        username: Annotated[
            str | None, Form(examples=["user@example.com"])
        ] = None,
        password: Annotated[str | None, Form(examples=["password"])] = None,
        refresh_token: Annotated[str | None, Form()] = None,
        scope: Annotated[
            str,
            Form(),
        ] = "",
        client_id: Annotated[
            str | None,
            Form(),
        ] = None,
        client_secret: Annotated[
            str | None,
            Form(),
        ] = None,
    ):
        match grant_type:
            case "password":
                if username is None or password is None:
                    raise ValidationError(
                        [
                            {
                                "loc": "form",
                                "msg": "Username and password are required",
                            }
                        ]
                    )
            case "refresh_token":
                if refresh_token is None:
                    raise ValidationError(
                        [
                            {
                                "loc": "form",
                                "msg": "Refresh token is required",
                            }
                        ]
                    )
            case _:
                assert_never(grant_type)

        self.refresh_token = refresh_token

        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )


def get_from_cookies(request: Request) -> str | None:
    return request.cookies.get(TOKEN_COOKIE_NAME)


def get_from_headers(request: Request) -> str | None:
    authorization = request.headers.get(TOKEN_HEADER_NAME)
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        return None
    return param


class OAuth2PasswordBearer(FastAPIOAuth2PasswordBearer):
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
