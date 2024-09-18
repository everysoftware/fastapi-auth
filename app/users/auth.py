from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request

from app.users.constants import TOKEN_HEADER_NAME, TOKEN_COOKIE_NAME
from app.users.exceptions import NoTokenProvided


def get_from_cookies(request: Request) -> str | None:
    return request.cookies.get(TOKEN_COOKIE_NAME)


def get_from_headers(request: Request) -> str | None:
    authorization = request.headers.get(TOKEN_HEADER_NAME)
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        return None
    return param


class BackendAuth:
    parsers = [get_from_cookies, get_from_headers]

    def __init__(self, *, auto_error: bool = True):
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> str | None:
        for parser in self.parsers:
            token = parser(request)
            if token:
                return token
        if self.auto_error:
            raise NoTokenProvided()
        else:
            return None
