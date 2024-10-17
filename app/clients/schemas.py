from typing import Any

from pydantic import field_validator

from app.db.schemas import IDModel, TimestampModel


class ClientRead(IDModel, TimestampModel):
    name: str
    client_id: str
    client_secret: str
    redirect_uris: list[str]
    is_active: bool

    @field_validator("redirect_uris", mode="before")
    def validate_redirect_uris(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.split(";")
        return v
