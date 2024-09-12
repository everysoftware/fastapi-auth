from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.admin.main import app as admin_app
from app.cache.lifetime import ping_redis
from app.config import settings
from app.exceptions import BackendError
from app.logging import logger
from app.routing import main_router
from app.schemas import BackendErrorResponse
from app.users.lifespan import register_default_users


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup tasks
    await register_default_users()
    await ping_redis()
    yield
    # Shutdown tasks
    # ...


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_title,
    version=settings.app_version,
    summary="No description",
    root_path="/api/v1",
)


@app.exception_handler(BackendError)
def backend_exception_handler(
    request: Request, ex: BackendError
) -> JSONResponse:
    logger.error(f"{request.method} {request.url} failed: {repr(ex)}")
    return JSONResponse(
        status_code=ex.status_code,
        content=BackendErrorResponse(
            msg=ex.message,
            code=ex.error_code,
        ).model_dump(mode="json"),
        headers=ex.headers,
    )


@app.exception_handler(Exception)
def unhandled_exception_handler(
    request: Request, ex: Exception
) -> JSONResponse:
    logger.exception(
        f"{request.method} {request.url} failed [UNHANDLED]: {repr(ex)}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=BackendErrorResponse(
            msg="Internal Server Error",
            code="unexpected_error",
        ).model_dump(mode="json"),
    )


app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=settings.cors.cors_origins,
    allow_origin_regex=settings.cors.cors_origin_regex,
    allow_credentials=True,
    allow_methods=settings.cors.cors_methods,
    allow_headers=settings.cors.cors_headers,
)
app.mount("/admin", admin_app)

app.include_router(main_router)
