from enum import StrEnum, auto
from typing import Optional

import pydantic
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


class OpenID(pydantic.BaseModel):
    """Class (schema) to represent information got from sso provider in a common form."""

    id: Optional[str] = None
    email: Optional[pydantic.EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    picture: Optional[str] = None
    provider: Optional[str] = None
