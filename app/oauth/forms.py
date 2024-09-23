from typing import Annotated

from fastapi import Form
from pydantic import AnyHttpUrl

from app.schemas import BackendBase


class SSOCallbackForm:
    def __init__(
        self,
        *,
        code: Annotated[str, Form()],
        redirect_uri: Annotated[AnyHttpUrl, Form()],
    ):
        self.code = code
        self.redirect_uri = redirect_uri


class SSOLoginParams(BackendBase):
    redirect_uri: AnyHttpUrl
    state: str = "default"
    redirect: bool = True
