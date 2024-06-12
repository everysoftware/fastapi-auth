from onepattern import DeclarativeBase, AlchemyEntity


class Base(DeclarativeBase):
    __abstract__ = True


class EntityBase(Base, AlchemyEntity):
    __abstract__ = True
