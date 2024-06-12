from sqlalchemy.orm import Mapped

from app.models import EntityBase


class Waffle(EntityBase):
    __tablename__ = "__test_waffles__"

    name: Mapped[str]
    age: Mapped[int]
