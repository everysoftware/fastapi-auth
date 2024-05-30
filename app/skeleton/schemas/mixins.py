import datetime
from abc import ABC

from pydantic import Field

from .base import SkeletonModel


# https://docs.pydantic.dev/latest/concepts/models/#abstract-base-classes


class MixinModel(SkeletonModel, ABC):
    """Base class for all mixins."""

    pass


class HasID(MixinModel):
    id: int = Field(ge=1)


class HasTimestamp(MixinModel):
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
    )


class SoftDeletable(MixinModel):
    deleted_at: datetime.datetime | None = Field(
        None,
    )


class EntityModel(HasID, HasTimestamp):
    pass
