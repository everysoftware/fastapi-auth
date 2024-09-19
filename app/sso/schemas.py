from enum import StrEnum, auto
from typing import Literal

import pydantic
from pydantic import AnyHttpUrl, ConfigDict

from app.schemas import BackendBase

type AnyUrl = pydantic.AnyHttpUrl | str


class DiscoveryDocument(BackendBase):
    authorization_endpoint: str | None = None
    token_endpoint: str | None = None
    userinfo_endpoint: str | None = None

    model_config = ConfigDict(extra="allow")


class SSOCallback(BackendBase):
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
    provider: str
    email: pydantic.EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    picture: str | None = None


class SSOName(StrEnum):
    google = auto()
    yandex = auto()
    telegram = auto()


class AuthorizationURL(BackendBase):
    url: str
