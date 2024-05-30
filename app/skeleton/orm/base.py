from enum import Enum
from typing import Any, Self

from pydantic import BaseModel
from sqlalchemy import BigInteger, inspect, Enum as SAEnum, MetaData
from sqlalchemy.orm import (
    DeclarativeBase,
)

type_map = {int: BigInteger, Enum: SAEnum(Enum, native_enum=False)}

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class SkeletonBase(DeclarativeBase):
    type_annotation_map = type_map
    metadata = metadata

    def update(self, attributes: BaseModel | dict[str, Any]) -> Self:
        """Update an object with given attribute values."""
        if isinstance(attributes, BaseModel):
            attributes = attributes.model_dump(exclude_unset=True)

        for name, value in attributes.items():
            setattr(self, name, value)

        return self

    def dump(self) -> dict[str, Any]:
        """Dump the object to a dictionary."""
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs  # noqa
        }
