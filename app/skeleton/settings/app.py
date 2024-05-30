from typing import Literal

from pydantic import Field

from app.skeleton import SkeletonModel


class App(SkeletonModel):
    title: str = "Test"
    version: str = "1.0.0"
    env: Literal["dev", "prod", "test"] = "dev"


class API(App):
    cors_origins: list[str] = Field(["*"])
    cors_headers: list[str] = Field(["*"])
    cors_methods: list[str] = Field(["*"])


class TelegramBot(App):
    token: str
