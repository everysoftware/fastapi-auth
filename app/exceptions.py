from enum import StrEnum

from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    pass


class CustomValidationError(RequestValidationError):
    def __init__(self, loc: list[str], msg: str):
        super().__init__([{"loc": loc, "msg": msg, "type": "custom"}])


class ErrorCode(StrEnum):
    pass
