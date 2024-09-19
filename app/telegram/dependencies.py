from typing import Annotated

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import Depends

from app.config import settings


def get_bot() -> Bot:
    return Bot(
        settings.auth.telegram_bot_token,
        default=DefaultBotProperties(),
    )


BotDep = Annotated[Bot, Depends(get_bot)]
