from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.admin.main import app as admin_app
from app.clients.lifespan import create_clients
from app.frontend.main import app as frontend_app
from app.cache.lifespan import ping_redis
from app.config import settings
from app.cors import setup_cors
from app.exc_handlers import setup_exceptions
from app.obs.setup import setup_obs
from app.routing import main_router
from app.users.lifespan import register_users


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup tasks
    await ping_redis()
    await register_users()
    await create_clients()
    yield
    # Shutdown tasks
    # ...


app = FastAPI(lifespan=lifespan)

api_app = FastAPI(
    title=settings.app_display_name,
    version=settings.app_version,
    summary="Modern authorization server",
    root_path="/api/v1",
)
api_app.include_router(main_router)

setup_cors(api_app)
setup_exceptions(api_app)
setup_obs(api_app)

app.mount("/api", api_app)
app.mount("/admin", admin_app)
app.mount("/", frontend_app)
