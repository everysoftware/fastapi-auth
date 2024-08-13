from app.db.schemas import Page, PageParams
from app.db.types import ID
from app.permissions.schemas import (
    PermissionUpdate,
    PermissionRead,
    PermissionCreate,
)
from app.service import Service


class PermissionService(Service):
    async def create(self, creation: PermissionCreate) -> PermissionRead:
        data = creation.model_dump()
        return await self.uow.permissions.create(**data)

    async def get(self, permission_id: ID) -> PermissionRead | None:
        return await self.uow.permissions.get(permission_id)

    async def update(
        self, permission_id: ID, update: PermissionUpdate
    ) -> PermissionRead:
        data = update.model_dump()
        return await self.uow.permissions.update(permission_id, data)

    async def delete(self, permission_id: ID) -> PermissionRead:
        return await self.uow.permissions.delete(permission_id)

    async def get_many(self, params: PageParams) -> Page[PermissionRead]:
        return await self.uow.permissions.get_many(params)
