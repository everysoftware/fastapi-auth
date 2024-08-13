from typing import Iterable

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from app.db.pagination import make_page
from app.db.repository import AlchemyGenericRepository
from app.db.schemas import Page
from app.db.types import ID
from app.permissions.models import PermissionOrm
from app.permissions.schemas import PermissionRead
from app.roles_permissions.models import RolePermissionOrm
from app.roles_permissions.schemas import RolePermissionRead


class RolePermissionRepository(AlchemyGenericRepository[RolePermissionRead]):
    model_type = RolePermissionOrm
    schema_type = RolePermissionRead

    async def get_permissions(self, role_id: ID) -> Page[PermissionRead]:
        stmt = select(PermissionOrm).join(
            RolePermissionOrm,
            (RolePermissionOrm.permission_id == PermissionOrm.id)
            & (RolePermissionOrm.role_id == role_id),
        )
        details = await self.session.scalars(stmt)
        return make_page(details, item_model=PermissionRead)

    async def set(
        self, role_id: ID, permissions: Iterable[ID]
    ) -> Page[PermissionRead]:
        stmt = delete(RolePermissionOrm).where(
            (RolePermissionOrm.role_id == role_id)
            & RolePermissionOrm.permission_id.notin_(permissions)
        )
        await self.session.execute(stmt)

        data = [{"role_id": role_id, "permission_id": p} for p in permissions]
        stmt = insert(RolePermissionOrm).on_conflict_do_nothing()
        await self.session.execute(stmt, data)

        return await self.get_permissions(role_id)
