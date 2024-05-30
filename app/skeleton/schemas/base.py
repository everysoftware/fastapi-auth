from abc import ABC
from typing import TypeVar, Type, Any

from pydantic import BaseModel, ConfigDict

Model = TypeVar("Model", bound=BaseModel)


class SkeletonModel(BaseModel, ABC):
    @classmethod
    def validate_or_none(
        cls: Type[Model], model: Any, **kwargs: Any
    ) -> Model | None:
        if model is None:
            return None

        return cls.model_validate(model, **kwargs)

    model_config = ConfigDict(from_attributes=True)
