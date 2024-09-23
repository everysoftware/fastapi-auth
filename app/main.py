from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.admin.main import app as admin_app
from app.cache.lifespan import ping_redis
from app.config import settings
from app.cors import setup_cors
from app.exceptions import setup_exceptions
from app.obs.setup import setup_obs
from app.routing import main_router
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
    title=settings.app_display_name,
    version=settings.app_version,
    summary="No description",
    root_path="/api/v1",
)

setup_cors(app)
setup_exceptions(app)
app.mount("/admin", admin_app)
setup_obs(app)

app.include_router(main_router)
