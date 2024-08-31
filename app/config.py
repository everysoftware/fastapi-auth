import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    title: str = "FastAPI"
    version: str = "0.1.0"
    env: Literal["dev", "prod", "test"] = "dev"
    debug: bool = False

    cors_headers: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_origins: list[str] = ["*"]
    cors_origin_regex: str | None = None

    db_dsn: str

    jwt_private_key: Path = Path("certs") / "jwt-private.pem"
    jwt_public_key: Path = Path("certs") / "jwt-public.pem"
    jwt_algorithm: str = "RS256"
    jwt_access_expire_minutes: int = 30 * 24 * 60
    jwt_refresh_expire_minutes: int = 15
    su_email: str = "admin@example.com"
    su_password: str

    model_config = SettingsConfigDict(extra="allow", env_prefix="app_")


CANCEL_VAR = "NO_ENV_FILE"
ENV_FILES = [".env"]


def load_env() -> None:
    if os.getenv(CANCEL_VAR):
        return None
    for file in ENV_FILES:
        if load_dotenv(file):
            return
    raise ValueError(f"Environment file not found: {ENV_FILES}")


load_env()
settings = AppSettings()
