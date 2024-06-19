from onepattern import AlchemyBase, AlchemyEntity


class Base(AlchemyBase):
    __abstract__ = True


class EntityBase(Base, AlchemyEntity):
    __abstract__ = True
