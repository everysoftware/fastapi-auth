from enum import StrEnum, auto

from pydantic import Field, EmailStr

from app.db.schemas import IDModel, TimestampModel
from app.schemas import Base


class UserBase(Base):
    email: EmailStr


class UserRead(UserBase, IDModel, TimestampModel):
    hashed_password: str | None = Field(None, exclude=True)
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(UserBase):
    password: str


class UserUpdate(Base):
    email: EmailStr | None = None
    password: str | None = None


class TokenInfo(Base):
    access_token: str


class AccessType(StrEnum):
    user = auto()
    superuser = auto()
