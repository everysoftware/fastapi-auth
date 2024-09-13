from enum import StrEnum, auto
from typing import Optional, Literal

import pydantic
from pydantic import AnyHttpUrl

from app.schemas import BackendBase


class SSOName(StrEnum):
    google = auto()
    yandex = auto()


class SSOCallback(BackendBase):
    grant_type: Literal["authorization_code"] = "authorization_code"
    code: str
    redirect_uri: AnyHttpUrl
    state: str | None = None
    scope: str | None = None
    pkce_code_verifier: str | None = None

    @property
    def scopes(self) -> list[str] | None:
        if self.scope is not None:
            return self.scope.split()
        return None


class SSOBearerToken(BackendBase):
    access_token: str
    token_type: Literal["Bearer", "bearer"] = "Bearer"
    id_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None
    scope: str | None = None

    @property
    def scopes(self) -> list[str] | None:
        if self.scope is not None:
            return self.scope.split()
        return None


class OpenID(BackendBase):
    id: str
    email: Optional[pydantic.EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    picture: Optional[str] = None
    provider: str
