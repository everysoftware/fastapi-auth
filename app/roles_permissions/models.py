from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import BaseOrm
from app.db.mixins import IDMixin, TimestampMixin
from app.db.types import ID


class RolePermissionOrm(BaseOrm, IDMixin, TimestampMixin):
    __tablename__ = "roles_permissions"

    role_id: Mapped[ID] = mapped_column(
        ForeignKey("roles.id", ondelete="cascade")
    )
    permission_id: Mapped[ID] = mapped_column(
        ForeignKey("permissions.id", ondelete="cascade")
    )

    __table_args__ = (UniqueConstraint("role_id", "permission_id"),)
