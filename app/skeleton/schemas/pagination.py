from typing import Generic, TypeVar, Literal

from pydantic import Field, computed_field, BaseModel

from .base import SkeletonModel


class PageParams(SkeletonModel):
    limit: int = Field(10, ge=0, le=100)
    offset: int = Field(0, ge=0)
    sort_by: Literal["updated_at", "created_at"] = "updated_at"
    order: Literal["asc", "desc"] = "desc"


# https://docs.pydantic.dev/latest/concepts/models/#generic-models


Model = TypeVar("Model", bound=BaseModel)


class Page(SkeletonModel, Generic[Model]):
    items: list[Model]

    @computed_field
    def total(self) -> int:
        return len(self.items)
