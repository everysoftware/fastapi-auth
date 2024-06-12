from typing import Type
from typing import TypeVar, Any

from fastabc import (
    Page as FAPage,
    PageParams as FAParams,
    EntityModel as FAEntityModel,
)
from pydantic import BaseModel
from pydantic import ConfigDict

Model = TypeVar("Model", bound=BaseModel)


class MainModel(BaseModel):
    @classmethod
    def validate_or_none(
        cls: Type[Model], model: Any, **kwargs: Any
    ) -> Model | None:
        if model is None:
            return None

        return cls.model_validate(model, **kwargs)

    model_config = ConfigDict(from_attributes=True)


Page = FAPage
PageParams = FAParams
EntityModel = FAEntityModel
