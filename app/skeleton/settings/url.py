from abc import ABC
from typing import Any

from pydantic import model_validator, SecretStr

from app.skeleton import SkeletonModel


class ConnectionUrl(SkeletonModel, ABC):
    host: str
    port: int
    username: str
    password: SecretStr

    # aliases
    user: str

    @model_validator(mode="before")
    def check_model(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "user" in data and "username" in data:
                raise ValueError(
                    "Cannot have both 'user' and 'username' in the same URL"
                )
            if "user" in data:
                data["username"] = data["user"]
            if "username" in data:
                data["user"] = data["username"]
        return data
