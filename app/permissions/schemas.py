from pydantic import computed_field

from app.db.schemas import IDModel, TimestampModel
from app.schemas import Base


class PermissionBase(Base):
    domain: str
    task: str


class PermissionRead(PermissionBase, IDModel, TimestampModel):
    @computed_field  # type: ignore
    @property
    def slug(self) -> str:
        return f"{self.domain}:{self.task}"


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(Base):
    domain: str
    task: str
