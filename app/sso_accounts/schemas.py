from pydantic import Field

from app.db.schemas import IDModel, TimestampModel
from app.db.types import ID
from app.schemas import BackendBase


class SSOAccountBase(BackendBase):
    provider: str
    account_id: str
    access_token: str | None = None
    expires_in: int | None = None
    scope: str | None = None
    id_token: str | None = None
    refresh_token: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    picture: str | None = None


class SSOAccountCreate(SSOAccountBase):
    pass


class SSOAccountRead(SSOAccountBase, IDModel, TimestampModel):
    user_id: ID
    access_token: str | None = Field(None, exclude=True)
    id_token: str | None = Field(None, exclude=True)
    refresh_token: str | None = Field(None, exclude=True)
