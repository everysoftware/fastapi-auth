from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = ".env"


class CORSSettings(BaseSettings):
    cors_headers: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_origins: list[str] = ["*"]
    cors_origin_regex: str | None = None

    model_config = SettingsConfigDict(extra="allow", env_file=ENV_FILE)


class DBSettings(BaseSettings):
    db_dsn: str = "postgresql+asyncpg://postgres:changethis@localhost:5432/app"

    model_config = SettingsConfigDict(extra="allow", env_file=ENV_FILE)


class AuthSettings(BaseSettings):
    jwt_issuer: str = "https://example.com"
    jwt_audience: list[str] = ["https://example.com"]
    jwt_private_key: Path = Path("certs") / "jwt-private.pem"
    jwt_public_key: Path = Path("certs") / "jwt-public.pem"
    jwt_algorithm: str = "RS256"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_minutes: int = 30 * 24 * 60  # 30 days

    su_email: str = "admin@example.com"
    su_password: str = "changethis"

    google_sso_enabled: bool = False
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None

    yandex_sso_enabled: bool = False
    yandex_client_id: str | None = None
    yandex_client_secret: str | None = None
    yandex_redirect_uri: str | None = None

    @model_validator(mode="after")
    def validate_google_sso(self) -> Self:
        if self.google_sso_enabled:
            assert self.google_client_id, "Google client ID is required"
            assert (
                self.google_client_secret
            ), "Google client secret is required"
            assert self.google_redirect_uri, "Google redirect URI is required"
        return self

    @model_validator(mode="after")
    def validate_yandex_sso(self) -> Self:
        if self.yandex_sso_enabled:
            assert self.yandex_client_id, "Yandex client ID is required"
            assert (
                self.yandex_client_secret
            ), "Yandex client secret is required"
            assert self.yandex_redirect_uri, "Yandex redirect URI is required"
        return self

    model_config = SettingsConfigDict(extra="allow", env_file=ENV_FILE)


class AppSettings(BaseSettings):
    app_title: str = "FastAPI"
    app_version: str = "0.1.0"
    app_env: Literal["dev", "prod", "test"] = "dev"
    app_debug: bool = False

    db: DBSettings = DBSettings()
    cors: CORSSettings = CORSSettings()
    auth: AuthSettings = AuthSettings()

    model_config = SettingsConfigDict(extra="allow", env_file=".env")


settings = AppSettings()
