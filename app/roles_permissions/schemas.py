from app.db.schemas import IDModel, TimestampModel
from app.db.types import ID
from app.permissions.schemas import PermissionRead
from app.roles.schemas import RoleRead
from app.schemas import Base


class RolePermissionRead(Base, IDModel, TimestampModel):
    role_id: ID
    permission_id: ID

    role: RoleRead | None = None
    permission: PermissionRead | None = None
