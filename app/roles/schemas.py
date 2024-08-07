from app.database.schemas import UUIDModel, TimestampModel
from app.schemas import Base


class RoleBase(Base):
    name: str
    description: str | None


class RoleRead(RoleBase, UUIDModel, TimestampModel):
    pass


class RoleCreate(RoleBase):
    pass


class RoleUpdate(Base):
    name: str
