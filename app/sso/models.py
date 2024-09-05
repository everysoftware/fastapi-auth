from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseOrm
from app.db.mixins import IDMixin, TimestampMixin


class OIDCAccountOrm(BaseOrm, IDMixin, TimestampMixin):
    __tablename__ = "oidc_accounts"

    user_id: Mapped[UUID] = mapped_column(index=True)
    provider: Mapped[str]
    account_id: Mapped[str | None]
    access_token: Mapped[str]
    id_token: Mapped[str | None]
    refresh_token: Mapped[str | None]

    # OpenID Connect claims
    email: Mapped[str | None] = mapped_column(index=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    display_name: Mapped[str | None]
    picture: Mapped[str | None]
