import datetime
import uuid
from enum import StrEnum, auto
from typing import Literal

from pydantic import Field, EmailStr, ConfigDict, field_serializer

from app.config import settings
from app.db.schemas import IDModel, TimestampModel
from app.db.types import ID
from app.schemas import BackendBase


class UserBase(BackendBase):
    email: EmailStr


class UserRead(UserBase, IDModel, TimestampModel):
    hashed_password: str | None = Field(None, exclude=True)
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(UserBase):
    password: str


class UserUpdate(BackendBase):
    email: EmailStr | None = None
    password: str | None = None


# AUTHORIZATION
ACCESS_HEADER_NAME = "Authorization"
REFRESH_HEADER_NAME = "Refresh-Token"
ACCESS_COOKIE_NAME = "access_token"


class TokenType(StrEnum):
    access = auto()
    refresh = auto()


class TokenParams(BackendBase):
    algorithm: str = settings.jwt_algorithm
    private_key: str = settings.jwt_private_key.read_text()
    public_key: str = settings.jwt_public_key.read_text()
    type: TokenType
    expires_in: datetime.timedelta


class JWTPayload(BackendBase):
    jti: str
    typ: TokenType
    sub: ID
    iat: datetime.datetime
    exp: datetime.datetime

    @field_serializer("iat", "exp", mode="plain")
    def datetime_to_timestamp(self, value: datetime.datetime) -> int:
        return int(value.timestamp())

    model_config = ConfigDict(extra="allow")


class EncodeJWTResponse(BackendBase):
    payload: JWTPayload
    token: str


class BearerToken(BackendBase):
    token_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str
    refresh_token: str | None = None
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class Role(StrEnum):
    user = auto()
    superuser = auto()
