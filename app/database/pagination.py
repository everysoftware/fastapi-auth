from __future__ import annotations

from typing import Iterable, Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.orm import DeclarativeBase

from app.database.schemas import PageParams, Page


def apply_params(
    params: PageParams, orm_model: type[DeclarativeBase], stmt: Select
) -> Select:
    order_by = []
    for item in params.sort_params:
        attr = getattr(orm_model, item.field)
        order_by.append(attr.asc() if item.order == "asc" else attr.desc())
    stmt = stmt.limit(params.limit).offset(params.offset).order_by(order_by)
    return stmt


ItemModel = TypeVar("ItemModel", bound=BaseModel)


def make_page(
    instances: Iterable[Any], item_model: type[ItemModel]
) -> Page[ItemModel]:
    items = [item_model.model_validate(instance) for instance in instances]
    return Page[ItemModel](items=items)
