from app.db.schemas import IDModel, TimestampModel
from app.db.types import ID
from app.schemas import BackendBase


class OIDCAccountBase(BackendBase):
    user_id: ID
    provider: str
    access_token: str
    id_token: str | None
    refresh_token: str | None
    email: str | None
    first_name: str | None
    last_name: str | None
    display_name: str | None
    picture: str | None


class OIDCAccountRead(OIDCAccountBase, IDModel, TimestampModel):
    pass
