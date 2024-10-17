from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.config import settings
from app.frontend.auth import router as auth_router

app = FastAPI(title=f"{settings.app_display_name} Frontend")

app.mount("/static", StaticFiles(directory="static"), name="static")

routers = [auth_router]
for router in routers:
    app.include_router(router)
