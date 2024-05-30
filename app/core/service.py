from abc import ABC, abstractmethod
from typing import Any

from app.core.uow import UOW


class Service(ABC):
    uow: UOW

    def __init__(self, uow: UOW):
        self.uow = uow


class CRUDService(Service, ABC):
    @abstractmethod
    async def create(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def update(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def delete(self, *args: Any, **kwargs: Any) -> Any:
        pass
