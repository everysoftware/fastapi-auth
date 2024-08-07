from typing import Any, cast

from sqlalchemy import select

from app.database import utils
from app.database.pagination import apply_params, make_page
from app.database.repository import AlchemyRepository
from app.database.schemas import PageParams, Page
from app.database.types import ID
from app.database.utils import validate
from app.permissions.models import PermissionOrm
from app.permissions.schemas import PermissionRead


class PermissionRepository(AlchemyRepository):
    async def create(self, **kwargs: Any) -> PermissionRead:
        user = PermissionOrm(**kwargs)
        self.session.add(user)
        await self.session.flush()
        return validate(user, PermissionRead)

    async def get(self, user_id: ID) -> PermissionRead | None:
        user = await self.session.get(PermissionOrm, user_id)
        return validate(user, PermissionRead)

    async def update(
        self, user_id: ID, data: dict[str, Any]
    ) -> PermissionRead:
        user = cast(
            PermissionOrm, await self.session.get_one(PermissionOrm, user_id)
        )
        utils.update_attrs(user, data)
        await self.session.flush()
        return validate(user, PermissionRead)

    async def delete(self, user_id: ID) -> PermissionRead:
        user = cast(
            PermissionOrm, await self.session.get_one(PermissionOrm, user_id)
        )
        await self.session.delete(user)
        await self.session.flush()
        return validate(user, PermissionRead)

    async def get_many(self, params: PageParams) -> Page[PermissionRead]:
        stmt = select(PermissionOrm)
        stmt = apply_params(params, PermissionOrm, stmt)
        result = await self.session.execute(stmt)
        return make_page(result.scalars(), item_model=PermissionRead)
