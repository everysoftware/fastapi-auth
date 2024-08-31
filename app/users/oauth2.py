from typing import Annotated, Literal

from fastapi import Form
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request

from app.users.exceptions import NoTokenProvided
from app.users.schemas import ACCESS_HEADER_NAME, ACCESS_COOKIE_NAME


class CustomOAuth2PasswordRequestForm:
    def __init__(
        self,
        *,
        grant_type: Annotated[
            Literal["password", "refresh_token"],
            Form(pattern="password|refresh_token"),
        ] = "password",
        username: Annotated[str | None, Form()] = "user@example.com",
        password: Annotated[str | None, Form()] = "password",
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
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.refresh_token = refresh_token
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


def get_from_cookies(request: Request) -> str | None:
    return request.cookies.get(ACCESS_COOKIE_NAME)


def get_from_headers(request: Request) -> str | None:
    authorization = request.headers.get(ACCESS_HEADER_NAME)
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        return None
    return param


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
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
