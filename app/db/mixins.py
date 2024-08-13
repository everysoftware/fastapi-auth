import datetime
import uuid

from sqlalchemy import func, Identity
from sqlalchemy.orm import mapped_column, Mapped

from app.db import utils
from app.db.types import ID


# https://docs.sqlalchemy.org/en/20/core/defaults.html
# https://docs.sqlalchemy.org/en/20/orm/declarative_config.html#abstract
# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#orm-declarative-mapped-column-type-map-pep593


class Mixin:
    pass


class IntIDMixin(Mixin):
    id: Mapped[int] = mapped_column(
        Identity(), primary_key=True, sort_order=-100
    )


class IDMixin(Mixin):
    id: Mapped[ID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        sort_order=-100,
    )


class TimestampMixin(Mixin):
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), sort_order=100
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=utils.naive_utc,
        sort_order=101,
    )


class SoftRemovalMixin(Mixin):
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        sort_order=102
    )
