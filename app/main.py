from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI

from app.settings import settings

# Routers
routers = []


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup tasks
    # ...
    yield
    # Shutdown tasks
    # ...


app = FastAPI(
    lifespan=lifespan,
    title=settings.app.title,
    version=settings.app.version,
    summary="A production-ready template for FastAPI projects.",
)

for router in routers:
    app.include_router(router, prefix="/api/v1")


@app.get("/healthcheck", include_in_schema=False)
def healthcheck() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/hc", include_in_schema=False)
def hc() -> dict[str, Any]:
    return {"status": "ok"}
