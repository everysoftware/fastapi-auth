from abc import ABC
from typing import assert_never

from aiogram import Bot
from fastapi import BackgroundTasks

from app.cache.adapter import CacheAdapter
from app.cache.dependencies import CacheDep
from app.db.dependencies import UOWDep
from app.db.uow import UOW
from app.mail.client import MailClient
from app.mail.dependencies import MailDep
from app.oauth.dependencies import (
    GoogleSSODep,
    YandexSSODep,
    TelegramSSODep,
    SSOName,
)
from app.oauth.interfaces import IOAuth2
from app.telegram.dependencies import BotDep


class Service(ABC):
    uow: UOW
    cache: CacheAdapter
    mail: MailClient
    bot: Bot
    google_sso: IOAuth2
    yandex_sso: IOAuth2
    telegram_sso: IOAuth2
    background: BackgroundTasks

    def __init__(
        self,
        uow: UOWDep,
        cache: CacheDep,
        mail: MailDep,
        bot: BotDep,
        google_sso: GoogleSSODep,
        yandex_sso: YandexSSODep,
        telegram_sso: TelegramSSODep,
        background: BackgroundTasks,
    ):
        self.uow = uow
        self.cache = cache
        self.mail = mail
        self.bot = bot
        self.google_sso = google_sso
        self.yandex_sso = yandex_sso
        self.telegram_sso = telegram_sso
        self.background = background

    def resolve_sso(self, provider: SSOName) -> IOAuth2:
        match provider:
            case SSOName.google:
                return self.google_sso
            case SSOName.yandex:
                return self.yandex_sso
            case SSOName.telegram:
                return self.telegram_sso
            case _:
                assert_never(provider)
