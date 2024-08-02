from __future__ import annotations


from pydantic import BaseModel
from pydantic import ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)
