from typing import Any

from fastapi import APIRouter, Depends
from starlette import status

from app.schemas import BackendErrorResponse
from app.sso.router import router as sso_accounts_router
from app.users.dependencies import GetCurrentUser
from app.users.router import auth_router, user_router, sso_router

protected_router = APIRouter(dependencies=[Depends(GetCurrentUser())])
protected_router.include_router(user_router)
protected_router.include_router(sso_accounts_router)

unprotected_router = APIRouter()
unprotected_router.include_router(auth_router)
unprotected_router.include_router(sso_router)

main_router = APIRouter(
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BackendErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": BackendErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": BackendErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BackendErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": BackendErrorResponse},
    },
)
main_router.include_router(unprotected_router)
main_router.include_router(protected_router)


@main_router.get("/healthcheck", include_in_schema=False)
def healthcheck() -> dict[str, Any]:
    return {"status": "ok"}


@main_router.get("/hc", include_in_schema=False)
def hc() -> dict[str, Any]:
    return {"status": "ok"}
