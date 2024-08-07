from pydantic import computed_field

from app.database.schemas import UUIDModel, TimestampModel
from app.schemas import Base


class PermissionBase(Base):
    domain: str
    task: str

    @computed_field  # type: ignore
    @property
    def slug(self) -> str:
        return f"{self.domain}:{self.task}"


class PermissionRead(PermissionBase, UUIDModel, TimestampModel):
    pass


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(Base):
    domain: str
    task: str
