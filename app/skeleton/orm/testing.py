from sqlalchemy.orm import Mapped

from .mixins import EntityBase


class TestUser(EntityBase):
    __tablename__ = "__test_users__"

    name: Mapped[str]
    age: Mapped[int]
