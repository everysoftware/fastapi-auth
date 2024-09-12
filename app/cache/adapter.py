import json
from typing import Any, cast as _cast

from redis.asyncio import Redis


class CacheAdapter:
    client: Redis
    key: str

    def __init__(self, redis: Redis, *, key: str = "fastapi"):
        self.client = redis
        self.key = key

    async def add[T](
        self, key: str, value: T, expire: int | None = None
    ) -> str:
        json_str = json.dumps(value, ensure_ascii=True)
        await self.client.set(f"{self.key}:{key}", json_str, ex=expire)
        return json_str

    async def get[T](
        self,
        key: str,
        cast: type[T] = Any,
    ) -> T | None:
        value = await self.client.get(f"{self.key}:{key}")
        if value is None:
            return None
        return _cast(cast, json.loads(value))

    async def keys(self, pattern: str) -> set[str]:
        keys = await self.client.keys(f"{self.key}:{pattern}")
        return set(keys)

    async def delete(self, key: str) -> Any:
        return await self.client.delete(f"{self.key}:{key}")
