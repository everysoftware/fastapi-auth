from pydantic import Field

from app.db.schemas import IDModel, TimestampModel
from app.db.types import ID
from app.schemas import BackendBase


class SSOAccountBase(BackendBase):
    user_id: ID
    provider: str
    access_token: str = Field(exclude=True)
    expires_in: int | None
    scope: str | None
    id_token: str | None = Field(exclude=True)
    refresh_token: str | None = Field(exclude=True)
    email: str | None
    first_name: str | None
    last_name: str | None
    display_name: str | None
    picture: str | None


class SSOAccountRead(SSOAccountBase, IDModel, TimestampModel):
    pass


class URLResponse(BackendBase):
    url: str
