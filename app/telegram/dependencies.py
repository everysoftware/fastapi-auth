from typing import Annotated, AsyncGenerator

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import Depends

from app.config import settings


async def get_bot() -> AsyncGenerator[Bot, None]:
    async with Bot(
        settings.telegram.bot_token,
        default=DefaultBotProperties(),
    ) as bot:
        yield bot


BotDep = Annotated[Bot, Depends(get_bot)]
