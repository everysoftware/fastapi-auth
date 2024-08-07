from pydantic import Field

from app.database.schemas import UUIDModel, TimestampModel
from app.schemas import Base


class UserBase(Base):
    email: str


class UserRead(UserBase, UUIDModel, TimestampModel):
    hashed_password: str | None = Field(None, exclude=True)
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(UserBase):
    password: str


class UserUpdate(Base):
    email: str | None = None
    password: str | None = None


class TokenInfo(Base):
    access_token: str
