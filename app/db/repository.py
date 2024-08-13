from abc import ABC
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import BaseOrm, utils
from app.db.exceptions import NoSuchEntity
from app.db.pagination import apply_params, make_page
from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.db.utils import validate
from app.schemas import Base


class AlchemyRepository(ABC):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session


class AlchemyGenericRepository[S: Base](AlchemyRepository):
    model_type: type[BaseOrm]
    schema_type: type[Base]

    async def create(self, **data: Any) -> S:
        instance = self.model_type(**data)
        self.session.add(instance)
        await self.session.flush()
        return validate(instance, self.schema_type)

    async def get(self, ident: ID) -> S | None:
        instance = await self.session.get(self.model_type, ident)
        return validate(instance, self.schema_type)

    async def get_one(self, ident: ID) -> S:
        result = await self.get(ident)
        if result is None:
            raise NoSuchEntity()
        return result

    async def update(self, ident: ID, data: dict[str, Any]) -> S:
        instance = cast(
            self.model_type, await self.session.get_one(self.model_type, ident)
        )
        utils.update_attrs(instance, data)
        await self.session.flush()
        return validate(instance, self.schema_type)

    async def delete(self, ident: ID) -> S:
        instance = cast(
            self.model_type, await self.session.get_one(self.model_type, ident)
        )
        await self.session.delete(instance)
        await self.session.flush()
        return validate(instance, self.schema_type)

    async def get_many(self, params: PageParams) -> Page[S]:
        stmt = select(self.model_type)
        stmt = apply_params(params, self.model_type, stmt)
        result = await self.session.scalars(stmt)
        return make_page(result, item_model=self.schema_type)
