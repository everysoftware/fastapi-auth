from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.cache.adapter import CacheAdapter
from app.config import settings

redis_client = Redis.from_url(settings.cache.redis_url)
cache = CacheAdapter(redis_client, key=settings.cache.redis_key)


def get_cache() -> CacheAdapter:
    return cache


CacheDep = Annotated[CacheAdapter, Depends(get_cache)]
