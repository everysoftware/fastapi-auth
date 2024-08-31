from pydantic import BaseModel
from pydantic import ConfigDict


class BackendBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BackendErrorResponse(BackendBase):
    message: str
    error_code: str
