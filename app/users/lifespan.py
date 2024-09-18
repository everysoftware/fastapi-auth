from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.cache.dependencies import cache
from app.config import settings
from app.db.dependencies import uow
from app.notifications.service import NotificationService
from app.users.service import UserService


@asynccontextmanager
async def users_ctx() -> AsyncGenerator[UserService, None]:
    async with uow:
        notifications = NotificationService(uow, cache)
        users = UserService(uow, cache, notifications=notifications)
        yield users


async def register_default_users() -> None:
    async with users_ctx() as users:
        user = await users.get_by_email(settings.auth.admin_email)
        if not user:
            await users.register(
                email=settings.auth.admin_email,
                password=settings.auth.admin_password,
                is_superuser=True,
            )

        # user
        user = await users.get_by_email("user@example.com")
        if not user:
            await users.register(email="user@example.com", password="password")
