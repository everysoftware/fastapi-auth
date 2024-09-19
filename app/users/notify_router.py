from fastapi import APIRouter
from starlette import status

from app.schemas import BackendOK, backend_ok
from app.users.dependencies import UserServiceDep, UserDep
from app.users.schemas import NotifyVia, VerifyToken

router = APIRouter(prefix="/notify", tags=["Notifications"])


@router.post("/code", status_code=status.HTTP_200_OK)
async def send_code(
    service: UserServiceDep,
    user: UserDep,
    via: NotifyVia = NotifyVia.email,
) -> BackendOK:
    await service.send_code(
        via=via, email=user.email, telegram_id=user.telegram_id
    )
    return backend_ok


@router.get("/code/verify", status_code=status.HTTP_200_OK)
async def verify_code(
    service: UserServiceDep,
    user: UserDep,
    code: str,
) -> VerifyToken:
    return await service.verify_code(user, code)
