from typing import Type
from typing import TypeVar, Any

from onepattern import (
    Page as OPPage,
    PageParams as OPParams,
    EntityModel as OPEntityModel,
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


Page = OPPage
PageParams = OPParams
EntityModel = OPEntityModel
