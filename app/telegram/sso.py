import datetime
import hashlib
import hmac
from typing import Any
from urllib.parse import urlencode

from aiogram import Bot
from pydantic import AnyHttpUrl

from app.config import settings
from app.sso.schemas import OpenID
from app.telegram.exceptions import (
    InvalidTelegramHash,
    TelegramAuthDataExpired,
)
from app.telegram.schemas import TelegramAuthData


def replace_localhost(url: Any) -> str:
    return str(url).replace("localhost", "127.0.0.1", 1)


class TelegramSSO:
    provider = "telegram"
    scope = ["write"]
    authorization_endpoint = "https://oauth.telegram.org/auth"

    bot: Bot

    def __init__(self, bot: Bot):
        self.bot = bot

    async def get_login_url(
        self,
        redirect_uri: AnyHttpUrl | str,
    ) -> str:
        redirect_uri = replace_localhost(redirect_uri)
        login_params = {
            "embed": 1,
            "bot_id": self.bot.id,
            "origin": redirect_uri,
            "request_access": self.scope,
        }
        return f"{self.authorization_endpoint}?{urlencode(login_params)}"

    async def validate_auth_data(
        self,
        auth_data: TelegramAuthData,
    ) -> OpenID:
        code_hash = auth_data.hash
        data_check_string = "\n".join(
            sorted(
                f"{k}={v}"
                for k, v in auth_data.model_dump(exclude={"hash"}).items()
            )
        )
        computed_hash = hmac.new(
            hashlib.sha256(self.bot.token.encode()).digest(),
            data_check_string.encode(),
            "sha256",
        ).hexdigest()
        if not hmac.compare_digest(computed_hash, code_hash):
            raise InvalidTelegramHash()
        dt = datetime.datetime.fromtimestamp(
            auth_data.auth_date, tz=datetime.UTC
        )
        now = datetime.datetime.now(tz=datetime.UTC)
        if now - dt > datetime.timedelta(
            seconds=settings.auth.telegram_auth_data_expire
        ):
            raise TelegramAuthDataExpired()
        first_name, last_name = (
            auth_data.first_name,
            auth_data.last_name,
        )
        display_name = (
            f"{first_name} {last_name}" if first_name else first_name
        )
        return OpenID(
            id=str(auth_data.id),
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            picture=auth_data.photo_url,
            provider=self.provider,
        )
