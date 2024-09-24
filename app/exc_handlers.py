from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.exceptions import BackendError, UnexpectedErrorResponse
from app.obs.logging import main_log
from app.schemas import BackendErrorResponse


def backend_exception_handler(
    request: Request, ex: BackendError
) -> JSONResponse:
    main_log.info(f'"{request.method} {request.url}" response: {repr(ex)}')
    return JSONResponse(
        status_code=ex.status_code,
        content=BackendErrorResponse(
            msg=ex.message,
            code=ex.error_code,
        ).model_dump(mode="json"),
        headers=ex.headers,
    )


def unhandled_exception_handler(
    request: Request, ex: Exception
) -> JSONResponse:
    main_log.exception(f'"{request.method} {request.url}" failed: {repr(ex)}')
    return UnexpectedErrorResponse()


def setup_exceptions(app: FastAPI) -> None:
    app.add_exception_handler(BackendError, backend_exception_handler)  # noqa
    app.add_exception_handler(Exception, unhandled_exception_handler)
