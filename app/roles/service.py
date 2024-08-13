from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.roles.schemas import RoleCreate, RoleRead, RoleUpdate
from app.service import Service


class RoleService(Service):
    async def create(self, data: RoleCreate) -> RoleRead:
        create_dict = data.model_dump(exclude={"permissions"})
        role = await self.uow.roles.create(**create_dict)
        role.permissions = await self.uow.roles_permissions.set(
            role.id, data.permissions
        )
        return role

    async def get(
        self, role_id: ID, with_permissions: bool = False
    ) -> RoleRead | None:
        role = await self.uow.roles.get(role_id)
        if with_permissions:
            role.permissions = (
                await self.uow.roles_permissions.get_permissions(role.id)
            )
        return role

    async def update(self, role_id: ID, data: RoleUpdate) -> RoleRead:
        update_data = data.model_dump(
            exclude={"permissions"}, exclude_none=True
        )
        role = await self.uow.roles.update(role_id, update_data)
        if data.permissions is not None:
            role.permissions = await self.uow.roles_permissions.set(
                role.id, data.permissions
            )
        return role

    async def delete(self, role_id: ID) -> RoleRead:
        return await self.uow.roles.delete(role_id)

    async def get_many(self, params: PageParams) -> Page[RoleRead]:
        return await self.uow.roles.get_many(params)
