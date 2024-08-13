from sqlalchemy.orm import mapped_column, Mapped

from app.db.base import BaseOrm
from app.db.mixins import TimestampMixin, IDMixin


class RoleOrm(BaseOrm, IDMixin, TimestampMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str | None]
