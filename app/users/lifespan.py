from app.config import settings
from app.db.connection import async_session_factory
from app.db.uow import UOW
from app.users.oidc import get_oidc
from app.users.schemas import UserCreate
from app.users.service import UserService


async def register_default_users() -> None:
    async with UOW(async_session_factory) as uow:
        oidc = get_oidc()
        users = UserService(uow, oidc=oidc)

        # superuser
        user = await users.get_by_email(settings.auth.su_email)
        if not user:
            await users.register(
                UserCreate(
                    email=settings.auth.su_email,
                    password=settings.auth.su_password,
                ),
                is_superuser=True,
            )

        # user
        user = await users.get_by_email("user@example.com")
        if not user:
            await users.register(
                UserCreate(email="user@example.com", password="password")
            )
