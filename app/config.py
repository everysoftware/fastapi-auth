import os
from pathlib import Path
from typing import Literal, Self

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

if not os.getenv("ENVIRONMENT_SET"):
    load_dotenv(".env")


class BackendSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")


class CORSSettings(BackendSettings):
    cors_headers: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_origins: list[str] = ["*"]
    cors_origin_regex: str | None = None


class DBSettings(BackendSettings):
    db_url: str = "postgresql+asyncpg://postgres:changethis@localhost:5432/app"


class AuthSettings(BackendSettings):
    jwt_issuer: str = "https://example.com"
    jwt_audience: list[str] = ["https://example.com"]
    jwt_private_key: Path = Path("certs") / "jwt-private.pem"
    jwt_public_key: Path = Path("certs") / "jwt-public.pem"
    jwt_algorithm: str = "RS256"
    jwt_access_expire: int = 15 * 60
    jwt_refresh_expire: int = 30 * 24 * 60  # 30 days

    admin_email: str = "admin@example.com"
    admin_password: str = "changethis"

    google_sso_enabled: bool = False
    google_client_id: str = ""
    google_client_secret: str = ""

    yandex_sso_enabled: bool = False
    yandex_client_id: str = ""
    yandex_client_secret: str = ""

    telegram_sso_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_auth_data_expire: int = 5 * 60

    code_length: int = 6
    code_expire: int = 5 * 60

    @model_validator(mode="after")
    def validate_google_sso(self) -> Self:
        if self.google_sso_enabled:
            assert self.google_client_id, "Google client ID is required"
            assert (
                self.google_client_secret
            ), "Google client secret is required"
        return self

    @model_validator(mode="after")
    def validate_yandex_sso(self) -> Self:
        if self.yandex_sso_enabled:
            assert self.yandex_client_id, "Yandex client ID is required"
            assert (
                self.yandex_client_secret
            ), "Yandex client secret is required"
        return self

    @model_validator(mode="after")
    def validate_telegram_sso(self) -> Self:
        if self.telegram_sso_enabled:
            assert self.telegram_bot_token, "Telegram bot token is required"
        return self


class MailSettings(BackendSettings):
    mail_enabled: bool = False
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "FastAPI"


class CacheSettings(BackendSettings):
    redis_key: str = "fastapi"
    redis_url: str = "redis://default+changethis@localhost:6379/0"


class AppSettings(BackendSettings):
    app_title: str = "FastAPI"
    app_version: str = "0.1.0"
    app_env: Literal["dev", "prod", "test"] = "dev"
    app_debug: bool = False

    db: DBSettings = DBSettings()
    cors: CORSSettings = CORSSettings()
    auth: AuthSettings = AuthSettings()
    mail: MailSettings = MailSettings()
    cache: CacheSettings = CacheSettings()


settings = AppSettings()
