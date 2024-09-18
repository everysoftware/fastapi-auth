from enum import StrEnum, auto
from typing import Literal

from pydantic import (
    Field,
    EmailStr,
    computed_field,
)

from app.db.schemas import IDModel, TimestampModel
from app.schemas import BackendBase


class UserBase(BackendBase):
    pass


class UserRead(UserBase, IDModel, TimestampModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    telegram_id: int | None = None
    hashed_password: str | None = Field(None, exclude=True)
    is_active: bool
    is_superuser: bool
    is_verified: bool

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_password(self) -> bool:
        return bool(self.hashed_password)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def display_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        return ""


class UserCreate(UserBase):
    first_name: str = Field(examples=["John"])
    last_name: str | None = Field(None, examples=["Doe"])
    email: EmailStr
    password: str


class UserUpdate(BackendBase):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    is_verified: bool | None = None


# AUTHORIZATION


class TokenType(StrEnum):
    access = auto()
    refresh = auto()
    verify = auto()


class GrantType(StrEnum):
    password = auto()
    refresh_token = auto()


class NotifyVia(StrEnum):
    email = auto()
    telegram = auto()


class BearerToken(BackendBase):
    token_id: str
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(
        description="Refresh token expiration time in seconds",
    )


class Role(StrEnum):
    user = auto()
    superuser = auto()


class VerifyToken(BackendBase):
    verify_token: str
    expires_in: int


class ResetPassword(BackendBase):
    email: str
    code: str
    password: str
