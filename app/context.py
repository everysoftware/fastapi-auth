from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import BackgroundTasks

from app.cache.dependencies import get_cache
from app.db.connection import async_session_factory
from app.db.uow import UOW
from app.mail.dependencies import get_mail
from app.oauth.dependencies import (
    get_google_sso,
    get_yandex_sso,
    get_telegram_sso,
)
from app.telegram.dependencies import get_bot
from app.users.service import UserService


@asynccontextmanager
async def uow_ctx() -> AsyncGenerator[UOW, None]:
    async with UOW(async_session_factory) as uow:
        yield uow


@asynccontextmanager
async def service_ctx() -> AsyncGenerator[dict[str, Any], None]:
    async with uow_ctx() as uow:
        bot = get_bot()
        yield {
            "uow": uow,
            "cache": get_cache(),
            "mail": get_mail(),
            "bot": bot,
            "google_sso": get_google_sso(),
            "yandex_sso": get_yandex_sso(),
            "telegram_sso": get_telegram_sso(bot),
            "background": BackgroundTasks(),
        }


@asynccontextmanager
async def users_ctx() -> AsyncGenerator[UserService, None]:
    async with service_ctx() as ctx:
        yield UserService(**ctx)
