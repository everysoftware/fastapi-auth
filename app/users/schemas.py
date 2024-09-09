import datetime
import uuid
from enum import StrEnum, auto
from typing import Literal

from pydantic import (
    Field,
    EmailStr,
    ConfigDict,
    field_serializer,
    computed_field,
)

from app.config import settings
from app.db.schemas import IDModel, TimestampModel
from app.schemas import BackendBase


class UserBase(BackendBase):
    pass


class UserRead(UserBase, IDModel, TimestampModel):
    email: EmailStr | None = None
    hashed_password: str | None = Field(None, exclude=True)
    is_active: bool
    is_superuser: bool
    is_verified: bool

    @computed_field
    def has_password(self) -> bool:
        return bool(self.hashed_password)


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(BackendBase):
    email: EmailStr | None = None
    password: str | None = None


# AUTHORIZATION


class TokenType(StrEnum):
    access = auto()
    refresh = auto()


class GrantType(StrEnum):
    password = auto()
    refresh_token = auto()


class TokenParams(BackendBase):
    issuer: str = settings.auth.jwt_issuer
    audience: list[str] = settings.auth.jwt_audience
    algorithm: str = settings.auth.jwt_algorithm
    private_key: str = settings.auth.jwt_private_key.read_text()
    public_key: str = settings.auth.jwt_public_key.read_text()
    type: TokenType
    expires_in: datetime.timedelta


class JWTClaims(BackendBase):
    jti: str = Field(default_factory=lambda: str(uuid.uuid4()))
    iss: str
    aud: list[str]
    typ: TokenType
    sub: str
    email: EmailStr | None = None
    iat: datetime.datetime
    nbf: datetime.datetime
    exp: datetime.datetime

    @field_serializer("iat", "exp", "nbf", mode="plain")
    def datetime_to_timestamp(self, value: datetime.datetime) -> int:
        return int(value.timestamp())

    model_config = ConfigDict(extra="allow")


class BearerToken(BackendBase):
    token_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(
        description="Refresh token expiration time in seconds",
    )


class Role(StrEnum):
    user = auto()
    superuser = auto()
