from enum import Enum
from typing import Any, Self
from uuid import UUID

from sqlalchemy import BigInteger, Enum as SAEnum, MetaData, Uuid, inspect
from sqlalchemy.orm import DeclarativeBase

type_map = {
    int: BigInteger,
    Enum: SAEnum(Enum, native_enum=False),
    UUID: Uuid(as_uuid=False),
}

NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)


class BaseOrm(DeclarativeBase):
    type_annotation_map = type_map
    metadata = metadata

    def dump(self) -> dict[str, Any]:
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs  # noqa
        }

    def update(self, **data: Any) -> Self:
        for name, value in data.items():
            setattr(self, name, value)
        return self

    def __repr__(self) -> str:
        return repr(self.dump())
