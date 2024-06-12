from fastabc.interfaces import AbstractGateway

from app.core.uow import UOW


class Gateway(AbstractGateway):
    # Services
    # ...

    def __init__(self, uow: UOW):
        super().__init__(uow)
