import os
from typing import Literal, Sequence

from dotenv import load_dotenv
from onepattern.settings import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class PgSettings(BaseSettings, PostgresDsn):
    model_config = SettingsConfigDict(extra="allow", env_prefix="postgres_")


class AppSettings(BaseSettings):
    title: str = "Test"
    version: str = "0.1.0"
    env: Literal["dev", "prod", "test"] = "dev"
    debug: bool = False

    cors_headers: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(extra="allow", env_prefix="app_")


class Settings:
    db: PgSettings
    app: AppSettings

    def __init__(self) -> None:
        self.db = PgSettings()
        self.app = AppSettings()


def load_env(
    env_files: Sequence[str] = (".dev.env", ".prod.env", ".env"),
    cancel_var: str | None = "NO_ENV_FILE",
) -> str | None:
    """
    Prioritized environment loading.

    Return the loaded file path or raise an exception if no file is found.
    Return `None` if the `cancel_var` is set in the environment.
    """
    if cancel_var and os.getenv(cancel_var):
        return None
    for file in env_files:
        if load_dotenv(file):
            return file
    raise ValueError(f"Environment file not found: {env_files}")


def get_settings() -> Settings:
    load_env()
    settings_ = Settings()
    return settings_


settings = get_settings()
