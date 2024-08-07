from sqlalchemy.orm import mapped_column, Mapped

from app.database.base import BaseOrm
from app.database.mixins import TimestampMixin, IDMixin


class RoleOrm(BaseOrm, IDMixin, TimestampMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    description: Mapped[str | None]
