from __future__ import annotations

from app.skeleton.orm import BaseUOW


class UOW(BaseUOW):
    async def on_open(self) -> None:
        pass
