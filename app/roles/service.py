from app.database.schemas import PageParams, Page
from app.database.types import ID
from app.roles.schemas import RoleCreate, RoleRead, RoleUpdate
from app.service import Service


class RoleService(Service):
    async def create(self, creation: RoleCreate) -> RoleRead:
        data = creation.model_dump()
        return await self.uow.roles.create(**data)

    async def get(self, role_id: ID) -> RoleRead | None:
        return await self.uow.roles.get(role_id)

    async def update(self, role_id: ID, update: RoleUpdate) -> RoleRead:
        data = update.model_dump()
        return await self.uow.roles.update(role_id, data)

    async def delete(self, role_id: ID) -> RoleRead:
        return await self.uow.roles.delete(role_id)

    async def get_many(self, params: PageParams) -> Page[RoleRead]:
        return await self.uow.roles.get_many(params)
