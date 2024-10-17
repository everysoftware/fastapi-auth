import os
from typing import Literal

from dotenv import load_dotenv

from app.clients.config import ClientSettings
from app.cache.config import CacheSettings
from app.db.config import DBSettings
from app.mail.config import MailSettings
from app.obs.config import ObservabilitySettings
from app.schemas import BackendSettings
from app.oauth.config import GoogleSettings, YandexSettings, TelegramSettings
from app.users.config import AuthSettings

if not os.getenv("ENVIRONMENT_SET"):
    load_dotenv(".env")


class CORSSettings(BackendSettings):
    cors_headers: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_origins: list[str] = ["*"]
    cors_origin_regex: str | None = None


class AppSettings(BackendSettings):
    app_name: str = "fastapiapp"
    app_display_name: str = "FastAPI App"
    app_version: str = "0.1.0"
    app_env: Literal["dev", "prod"] = "dev"
    app_debug: bool = False

    db: DBSettings = DBSettings()

    cache: CacheSettings = CacheSettings()
    auth: AuthSettings = AuthSettings()
    mail: MailSettings = MailSettings()
    cors: CORSSettings = CORSSettings()
    client: ClientSettings = ClientSettings()
    google: GoogleSettings = GoogleSettings()
    yandex: YandexSettings = YandexSettings()
    telegram: TelegramSettings = TelegramSettings()
    obs: ObservabilitySettings = ObservabilitySettings()


settings = AppSettings()
