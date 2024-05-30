from abc import ABC
from typing import TypeVar, Generic, Sequence, Any, cast

from sqlalchemy import (
    select,
    func,
    ColumnElement,
    BinaryExpression,
    UnaryExpression,
    insert,
    update,
)
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption

from .base import SkeletonBase
from ..schemas import PageParams

Model = TypeVar("Model", bound=SkeletonBase)
IdLike = Any | tuple[Any, ...]
WhereClause = Sequence[BinaryExpression[bool] | ColumnElement[bool]]
OrderBy = Sequence[UnaryExpression[Any] | ColumnElement[Any]]
T = TypeVar("T")


class BaseRepository(Generic[Model], ABC):
    model_type: type[Model]
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, *instances: Model) -> None:
        """Add an instance in the session."""
        self.session.add_all(instances)

    async def insert(
        self,
        *instances: Model,
    ) -> None:
        """Insert instances into the database."""
        if not instances:
            return
        stmt = insert(self.model_type)
        instance_dicts = [instance.dump() for instance in instances]
        await self.session.execute(stmt, instance_dicts)

    async def insert_and_return(
        self,
        *instances: Model,
        sort: bool = True,
    ) -> list[Model]:
        """Insert instances into the database and return them."""
        if not instances:
            return []
        stmt = insert(self.model_type).returning(
            self.model_type,
            sort_by_parameter_order=sort,
        )
        instance_dicts = [instance.dump() for instance in instances]
        scalars = await self.session.scalars(stmt, instance_dicts)
        return list(scalars)

    async def get(
        self, ident: IdLike, options: Sequence[ORMOption] | None = None
    ) -> Model | None:
        """Get an instance by ID. Return `None` if not found."""
        return await self.session.get(self.model_type, ident, options=options)

    async def get_one(
        self, ident: IdLike, options: Sequence[ORMOption] | None = None
    ) -> Model:
        """Get an instance by ID. Raise `sqlalchemy.exc.NoResultFound` if not found."""
        return await self.session.get_one(
            self.model_type, ident, options=options
        )

    async def get_many(
        self,
        *,
        where: WhereClause | None = None,
        group_by: Sequence[ColumnElement[Any]] | None = None,
        having: WhereClause | None = None,
        distinct: Sequence[ColumnElement[Any]] | None = None,
        order_by: OrderBy | None = None,
        limit: int | None = 10,
        offset: int | None = None,
    ) -> list[Model]:
        """Get instances from the database that meet the condition."""
        stmt = select(self.model_type)
        if where is not None:
            stmt = stmt.where(*where)
        if group_by is not None:
            stmt = stmt.group_by(*group_by)
        if having is not None:
            stmt = stmt.having(*having)
        if distinct is not None:
            stmt = stmt.distinct(*distinct)
        if order_by is not None:
            stmt = stmt.order_by(*order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        instances = list(result.scalars().all())
        return instances

    async def paginate(
        self,
        params: PageParams,
        where: WhereClause | None = None,
        group_by: Sequence[ColumnElement[Any]] | None = None,
        having: WhereClause | None = None,
        distinct: Sequence[ColumnElement[Any]] | None = None,
    ) -> list[Model]:
        """Paginate instances from the database."""
        attr = getattr(self.model_type, params.sort_by)
        order_by = [attr.desc() if params.order == "desc" else attr.asc()]
        return await self.get_many(
            where=where,
            group_by=group_by,
            having=having,
            distinct=distinct,
            limit=params.limit,
            offset=params.offset,
            order_by=order_by,
        )

    async def get_by_where(
        self, where: WhereClause | None = None
    ) -> Model | None:
        """
        Get instance from the database that meets the condition.

        Return None if not found.
        Raise `sqlalchemy.exc.MultipleResultsFound` if more than one found.
        """
        model_list = await self.get_many(where=where, limit=2)

        if not model_list:
            return None

        if len(model_list) > 1:
            raise MultipleResultsFound()

        return model_list[0]

    async def get_one_by_where(
        self, where: WhereClause | None = None
    ) -> Model:
        """
        Get instance from the database that meets the condition.

        Raise `sqlalchemy.exc.NoResultFound` if not found.
        Raise `sqlalchemy.exc.MultipleResultsFound` if more than one found.
        """
        instance = await self.get_by_where(where)

        if not instance:
            raise NoResultFound()

        return instance

    async def update(self, *instances: Model) -> None:
        """Update instances in the database."""
        stmt = update(self.model_type)
        dicts = [instance.dump() for instance in instances]
        await self.session.execute(stmt, dicts)

    async def merge(self, instance: Model) -> Model:
        """Merge an instance with the corresponding session state."""
        return await self.session.merge(instance)

    async def delete(self, model: Model) -> None:
        """Delete an instance from the session."""
        await self.session.delete(model)

    async def count(self, where: WhereClause) -> int:
        """Count instances in the database that meets the condition."""
        stmt = select(func.total(self.model_type)).where(*where)
        result = await self.session.execute(stmt)
        scalar = cast(int, result.scalar_one())
        return scalar

    async def max(self, attribute: ColumnElement[T]) -> T:
        """Get the maximum value of an attribute from the database."""
        stmt = select(func.max(attribute))
        result = await self.session.execute(stmt)
        scalar = result.scalar_one()
        return scalar

    async def min(self, attribute: ColumnElement[T]) -> T:
        """Get the minimum value of an attribute from the database."""
        stmt = select(func.min(attribute))
        result = await self.session.execute(stmt)
        scalar = result.scalar_one()
        return scalar
