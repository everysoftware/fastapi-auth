from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.sso.exceptions import SSODisabled
from app.telegram.sso import TelegramSSO

bot = Bot(
    settings.auth.telegram_bot_token,
    default=DefaultBotProperties(),
)


def get_telegram_sso() -> TelegramSSO:
    if not settings.auth.telegram_sso_enabled:
        raise SSODisabled()
    return TelegramSSO(bot)
