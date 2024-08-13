from app.db.repository import AlchemyGenericRepository
from app.roles.models import RoleOrm
from app.roles.schemas import RoleRead


class RoleRepository(AlchemyGenericRepository[RoleRead]):
    model_type = RoleOrm
    schema_type = RoleRead
