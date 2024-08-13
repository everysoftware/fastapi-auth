from abc import ABC

from app.db.uow import UOW


class Service(ABC):
    uow: UOW

    def __init__(self, uow: UOW):
        self.uow = uow
