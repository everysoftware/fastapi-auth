from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import BackendErrorResponse


class BackendError(Exception):
    message: str = "Internal server error"
    error_code: str = "unknown_error"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    headers: dict[str, str] | None = None

    def __init__(
        self,
        *,
        message: str | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
    ):
        if message is not None:
            self.message = message
        if error_code is not None:
            self.error_code = error_code
        if status_code is not None:
            self.status_code = status_code
        if headers is not None:
            self.headers = headers
        super().__init__(
            self.message, self.error_code, self.status_code, self.headers
        )  # make exception picklable (fill args member)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}(message="{self.message}", error_code={self.error_code}, status_code={self.status_code})'


class UnexpectedErrorResponse(JSONResponse):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=BackendErrorResponse(
                msg="Internal Server Error",
                code="unexpected_error",
            ).model_dump(mode="json"),
        )


class ValidationError(RequestValidationError):
    pass


class InvalidRequest(ValidationError):
    def __init__(self, msg: str) -> None:
        super().__init__(
            [{"loc": "request", "msg": msg, "type": "invalid_request"}]
        )
