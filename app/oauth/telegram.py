import datetime
import hashlib
import hmac
from typing import Any
from urllib.parse import urlencode

from aiogram import Bot

from app.schemas import BackendBase
from app.oauth.exceptions import (
    InvalidTelegramHash,
    TelegramAuthDataExpired,
    Unauthorized,
)
from app.oauth.interfaces import IOAuth2
from app.oauth.schemas import OpenID, AnyUrl, DiscoveryDocument, SSOBearerToken


class TelegramAuthData(BackendBase):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


# Telegram disallow localhost as origin
def replace_localhost(url: Any) -> str:
    return str(url).replace("localhost", "127.0.0.1", 1)


class TelegramOAuth2(IOAuth2):
    provider = "telegram"
    scope = ["write"]
    bot: Bot
    auth_expire: int
    auth_data: TelegramAuthData | None = None

    def __init__(
        self,
        bot: Bot,
        redirect_uri: AnyUrl | None = None,
        scope: list[str] | None = None,
        *,
        auth_expire: int = 5 * 60,
    ):
        super().__init__(str(bot.id), bot.token, redirect_uri, scope)
        self.bot = bot
        self.auth_expire = auth_expire

    async def discover(self) -> DiscoveryDocument:
        return DiscoveryDocument(
            authorization_endpoint="https://oauth.telegram.org/auth"
        )

    async def get_login_url(
        self,
        *,
        redirect_uri: AnyUrl | None = None,
        params: dict[str, Any] | None = None,
        state: str | None = None,
    ) -> str:
        params = params or {}
        redirect_uri = replace_localhost(redirect_uri or self.redirect_uri)
        login_params = {
            "bot_id": self.bot.id,
            "origin": redirect_uri,
            "request_access": self.scope,
            **params,
        }
        return f"{await self.authorization_endpoint}?{urlencode(login_params)}"

    async def openid_from_response(
        self,
        response: dict[Any, Any],
    ) -> OpenID:
        first_name, last_name = (
            response["first_name"],
            response.get("last_name"),
        )
        display_name = (
            f"{first_name} {last_name}" if first_name else first_name
        )
        return OpenID(
            id=str(response["id"]),
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            picture=response.get("photo_url"),
            provider=self.provider,
        )

    async def login(
        self,
        callback: TelegramAuthData,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> SSOBearerToken:
        self.auth_data = callback
        response = callback.model_dump()
        code_hash = response.pop("hash")
        data_check_string = "\n".join(
            sorted(f"{k}={v}" for k, v in response.items())
        )
        computed_hash = hmac.new(
            hashlib.sha256(self.client_secret.encode()).digest(),
            data_check_string.encode(),
            "sha256",
        ).hexdigest()
        if not hmac.compare_digest(computed_hash, code_hash):
            raise InvalidTelegramHash()
        dt = datetime.datetime.fromtimestamp(
            response["auth_date"], tz=datetime.UTC
        )
        now = datetime.datetime.now(tz=datetime.UTC)
        if now - dt > datetime.timedelta(seconds=self.auth_expire):
            raise TelegramAuthDataExpired()
        self._token = SSOBearerToken(access_token=callback.hash)
        return self.token

    async def get_userinfo_response(
        self,
        *,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if self.auth_data is None:
            raise Unauthorized
        return self.auth_data.model_dump()
