from sqlalchemy import Boolean
from sqlalchemy.orm import mapped_column, Mapped

from app.db.base import BaseOrm
from app.db.mixins import TimestampMixin, IDMixin


class UserOrm(BaseOrm, IDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str | None] = mapped_column(index=True)
    hashed_password: Mapped[str | None] = mapped_column()
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
