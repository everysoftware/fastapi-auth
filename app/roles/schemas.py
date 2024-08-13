from app.db.schemas import IDModel, TimestampModel, Page
from app.db.types import ID
from app.permissions.schemas import PermissionRead
from app.schemas import Base


class RoleBase(Base):
    name: str
    description: str | None


class RoleRead(RoleBase, IDModel, TimestampModel):
    permissions: Page[PermissionRead] | None = None


class RoleAddPermissions(Base):
    permissions: list[ID] | None = None


class RoleCreate(RoleBase, RoleAddPermissions):
    pass


class RoleUpdate(RoleAddPermissions):
    name: str | None = None
    description: str | None = None
