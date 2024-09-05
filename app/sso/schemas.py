from enum import StrEnum, auto

from pydantic import AnyUrl

from app.schemas import BackendBase


class SSOName(StrEnum):
    google = auto()
    yandex = auto()


class SSOCallback(BackendBase):
    code: str
    url: AnyUrl
    state: str | None = None
    pkce_code_verifier: str | None = None
