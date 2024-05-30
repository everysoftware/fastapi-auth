from pydantic_settings import BaseSettings, SettingsConfigDict

from app.skeleton.settings import Postgres, API, load_env


class PgSettings(BaseSettings, Postgres):
    model_config = SettingsConfigDict(extra="allow", env_prefix="postgres_")


class AppSettings(BaseSettings, API):
    model_config = SettingsConfigDict(extra="allow", env_prefix="app_")


class Settings:
    db: PgSettings
    app: AppSettings

    def __init__(self) -> None:
        self.db = PgSettings()
        self.app = AppSettings()


def get_settings() -> Settings:
    load_env()
    settings_ = Settings()
    return settings_


settings = get_settings()
