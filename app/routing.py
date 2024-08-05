from typing import Any

from fastapi import APIRouter, Depends

from app.users.dependencies import get_current_user
from app.users.router import auth_router, user_router

protected_router = APIRouter(dependencies=[Depends(get_current_user)])
protected_router.include_router(user_router)

main_router = APIRouter()
main_router.include_router(auth_router)
main_router.include_router(protected_router)


@main_router.get("/healthcheck", include_in_schema=False)
def healthcheck() -> dict[str, Any]:
    return {"status": "ok"}


@main_router.get("/hc", include_in_schema=False)
def hc() -> dict[str, Any]:
    return {"status": "ok"}
