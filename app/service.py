from abc import ABC

from app.database.uow import UOW


class Service(ABC):
    uow: UOW

    def __init__(self, uow: UOW):
        self.uow = uow
