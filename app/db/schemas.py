from __future__ import annotations

import datetime
from typing import Literal, cast

from pydantic import Field, computed_field, UUID4

from app.schemas import BackendBase

type OrderType = Literal["asc", "desc"]


class IDModel(BackendBase):
    id: UUID4


class TimestampModel(BackendBase):
    created_at: datetime.datetime
    updated_at: datetime.datetime


class SortParam(BackendBase):
    field: str
    order: OrderType = "asc"

    @classmethod
    def from_str(cls, value: str) -> SortParam:
        values = value.lower().split(":")
        if len(values) == 1:
            return SortParam(field=values[0])
        if len(values) == 2 and values[1] in ["asc", "desc"]:
            return SortParam(field=values[0], order=cast(OrderType, values[1]))
        raise ValueError(f"Invalid sort param: {value}")


class PageParams(BackendBase):
    limit: int = Field(10, ge=0, le=1000)
    offset: int = Field(0, ge=0)
    sort: str = "updated_at:desc"

    @computed_field  # type: ignore
    @property
    def sort_params(self) -> list[SortParam]:
        sort = self.sort.split(",")
        return [SortParam.from_str(i) for i in sort]


class Page[T: BackendBase](BackendBase):
    items: list[T]

    @computed_field  # type: ignore
    @property
    def total(self) -> int:
        return len(self.items)
