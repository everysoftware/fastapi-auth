from typing import Self

from pydantic import model_validator
from pydantic_settings import SettingsConfigDict

from app.config import BackendSettings
from app.schemas import BackendBase


class SSOSettingsMixin(BackendBase):
    sso: bool = False
    client_id: str = ""
    client_secret: str = ""

    @model_validator(mode="after")
    def validate(self) -> Self:
        if self.sso:
            assert self.client_id, "Client ID is required"
            assert self.client_secret, "Client secret is required"
        return self


class GoogleSettings(BackendSettings, SSOSettingsMixin):
    model_config = SettingsConfigDict(env_prefix="google_")


class YandexSettings(BackendSettings, SSOSettingsMixin):
    model_config = SettingsConfigDict(env_prefix="yandex_")


class TelegramSettings(BackendSettings):
    sso: bool = False
    bot_token: str = ""
    expire: int = 5 * 60

    model_config = SettingsConfigDict(env_prefix="telegram_")
