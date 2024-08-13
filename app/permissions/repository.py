from app.db.repository import AlchemyGenericRepository
from app.permissions.models import PermissionOrm
from app.permissions.schemas import PermissionRead


class PermissionRepository(AlchemyGenericRepository[PermissionRead]):
    model_type = PermissionOrm
    schema_type = PermissionRead
