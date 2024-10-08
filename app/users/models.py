from sqlalchemy import Boolean
from sqlalchemy.orm import mapped_column, Mapped

from app.db.base import BaseOrm
from app.db.mixins import TimestampMixin, IDMixin


class UserOrm(BaseOrm, IDMixin, TimestampMixin):
    __tablename__ = "users"

    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    email: Mapped[str | None] = mapped_column(index=True)
    telegram_id: Mapped[int | None] = mapped_column(index=True)
    hashed_password: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
