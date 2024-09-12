from abc import ABC

from app.cache.adapter import CacheAdapter
from app.cache.dependencies import CacheDep
from app.db.dependencies import UOWDep
from app.db.uow import UOW


class Service(ABC):
    uow: UOW
    cache: CacheAdapter

    def __init__(self, uow: UOWDep, cache: CacheDep):
        self.uow = uow
        self.cache = cache
