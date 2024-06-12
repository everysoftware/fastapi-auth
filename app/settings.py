from fastabc.settings import PostgresDsn, APIModel, load_env
from pydantic_settings import BaseSettings, SettingsConfigDict


class PgSettings(BaseSettings, PostgresDsn):
    model_config = SettingsConfigDict(extra="allow", env_prefix="postgres_")


class AppSettings(BaseSettings, APIModel):
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
