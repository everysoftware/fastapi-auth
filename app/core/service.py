from abc import ABC

from app.core.uow import UOW


class Service(ABC):
    uow: UOW

    def __init__(self, uow: UOW):
        self.uow = uow
