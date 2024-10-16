from abc import ABC
from typing import Any, Iterable, overload

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import BaseOrm
from app.db.schemas import PageParams, Page
from app.db.types import ID
from app.schemas import BackendBase


class BaseAlchemyRepository(ABC):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session


class AlchemyRepository[M: BaseOrm, S: BackendBase](BaseAlchemyRepository):
    model_type: type[M]
    schema_type: type[S]

    async def create(self, **data: Any) -> S:
        instance = self.model_type(**data)
        self.session.add(instance)
        await self.session.flush()
        return self.schema_type.model_validate(instance)

    async def get(self, ident: ID) -> S | None:
        instance = await self.session.get(self.model_type, ident)
        if instance is None:
            return None
        return self.schema_type.model_validate(instance)

    async def update(self, ident: ID, **data: Any) -> S:
        instance = await self.session.get_one(self.model_type, ident)  # type: BaseOrm
        instance.update(**data)
        await self.session.flush()
        return self.schema_type.model_validate(instance)

    async def delete(self, ident: ID) -> S:
        instance = await self.session.get_one(self.model_type, ident)
        await self.session.delete(instance)
        await self.session.flush()
        return self.schema_type.model_validate(instance)

    @overload
    def build_pagination_query[Q: Select[Any]](
        self, params: PageParams, stmt: Q
    ) -> Q: ...

    @overload
    def build_pagination_query(
        self, params: PageParams, stmt: None = None
    ) -> Select[Any]: ...

    def build_pagination_query(
        self, params: PageParams, stmt: Select[Any] | None = None
    ) -> Select[Any]:
        order_by = []
        for item in params.sort_params:
            attr = getattr(self.model_type, item.field)
            order_by.append(attr.asc() if item.order == "asc" else attr.desc())
        if stmt is None:
            stmt = select(self.model_type)
        stmt = (
            stmt.limit(params.limit).offset(params.offset).order_by(*order_by)
        )
        return stmt

    def validate_page(self, instances: Iterable[Any]) -> Page[S]:  # noqa
        items = [
            self.schema_type.model_validate(instance) for instance in instances
        ]
        return Page(items=items)

    async def get_many(self, params: PageParams) -> Page[S]:  # noqa
        stmt = self.build_pagination_query(params)
        result = await self.session.scalars(stmt)
        return self.validate_page(result)
