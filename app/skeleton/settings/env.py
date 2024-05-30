import os
from typing import Sequence

from dotenv import load_dotenv

from app.skeleton.exceptions import SettingsNotFound


def load_env(
    env_files: Sequence[str] = (".dev.env", ".prod.env", ".env"),
    no_env_file_var: str = "NO_ENV_FILE",
) -> None:
    if os.getenv(no_env_file_var):
        return
    for file in env_files:
        if load_dotenv(file):
            return
    raise SettingsNotFound(f"Settings file not found: {env_files}")
