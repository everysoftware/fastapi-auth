from typing import Any, cast

from sqlalchemy import select

from app.database import utils
from app.database.pagination import apply_params, make_page
from app.database.repository import AlchemyRepository
from app.database.schemas import PageParams, Page
from app.database.types import ID
from app.database.utils import validate
from app.permissions.schemas import PermissionRead
from app.roles.models import RoleOrm
from app.roles.schemas import RoleRead


class RoleRepository(AlchemyRepository):
    async def create(self, **kwargs: Any) -> RoleRead:
        role = RoleOrm(**kwargs)
        self.session.add(role)
        await self.session.flush()
        return validate(role, RoleRead)

    async def get(self, user_id: ID) -> RoleRead | None:
        role = await self.session.get(RoleOrm, user_id)
        return validate(role, RoleRead)

    async def update(self, user_id: ID, data: dict[str, Any]) -> RoleRead:
        role = cast(RoleOrm, await self.session.get_one(RoleOrm, user_id))
        utils.update_attrs(role, data)
        await self.session.flush()
        return validate(role, RoleRead)

    async def delete(self, user_id: ID) -> RoleRead:
        role = cast(RoleOrm, await self.session.get_one(RoleOrm, user_id))
        await self.session.delete(role)
        await self.session.flush()
        return validate(role, RoleRead)

    async def get_many(self, params: PageParams) -> Page[PermissionRead]:
        stmt = select(RoleOrm)
        stmt = apply_params(params, RoleOrm, stmt)
        result = await self.session.execute(stmt)
        return make_page(result.scalars(), item_model=PermissionRead)
