from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from app.database.base import BaseOrm
from app.database.mixins import TimestampMixin, IDMixin


class PermissionOrm(BaseOrm, IDMixin, TimestampMixin):
    __tablename__ = "permissions"

    domain: Mapped[str] = mapped_column(index=True, nullable=False)
    task: Mapped[str] = mapped_column(index=True, nullable=False)

    __table_args__ = (UniqueConstraint("domain", "task"),)
