import datetime
from typing import Any, overload

from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase

type Data = BaseModel | dict[str, Any]


def naive_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


def dump(instance: DeclarativeBase) -> dict[str, Any]:
    return {
        c.key: getattr(instance, c.key)
        for c in inspect(instance).mapper.column_attrs  # noqa
    }


def to_dict(obj: DeclarativeBase | Data | None) -> dict[str, Any]:
    if isinstance(obj, DeclarativeBase):
        return dump(obj)
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return obj
    elif obj is None:
        return {}
    raise ValueError(f"Cannot convert {obj} (type: {type(obj)}) to dict")


def update_attrs[T](obj: T, data: Data | None = None, **attrs: Any) -> T:
    if isinstance(data, BaseModel):
        obj_dict = data.model_dump(exclude_unset=True)
    elif isinstance(data, dict):
        obj_dict = data
    else:
        raise ValueError(
            f"Cannot update {obj} with {data} (type: {type(data)})"
        )
    obj_dict |= attrs
    for name, value in obj_dict.items():
        setattr(obj, name, value)
    return obj


@overload
def validate[ResponseModel: BaseModel](
    instance: DeclarativeBase, response_model: type[ResponseModel]
) -> ResponseModel: ...


@overload
def validate[ResponseModel: BaseModel](
    instance: DeclarativeBase | None, response_model: type[ResponseModel]
) -> ResponseModel | None: ...


def validate[ResponseModel: BaseModel](
    instance: DeclarativeBase | None, response_model: type[ResponseModel]
) -> ResponseModel | None:
    if instance is None:
        return None
    return response_model.model_validate(instance)
