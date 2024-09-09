from app.db.schemas import IDModel, TimestampModel
from app.db.types import ID
from app.schemas import BackendBase


class SSOAccountBase(BackendBase):
    user_id: ID
    provider: str
    access_token: str
    expires_in: int | None
    scope: str | None
    id_token: str | None
    refresh_token: str | None
    email: str | None
    first_name: str | None
    last_name: str | None
    display_name: str | None
    picture: str | None


class OIDCAccountRead(SSOAccountBase, IDModel, TimestampModel):
    pass
