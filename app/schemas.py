from pydantic import BaseModel
from pydantic import ConfigDict


class BackendBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BackendErrorResponse(BackendBase):
    msg: str
    code: str


class BackendOK(BackendErrorResponse):
    msg: str = "Success"
    code: str = "ok"


backend_ok = BackendOK()
