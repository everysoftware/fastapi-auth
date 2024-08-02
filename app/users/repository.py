from typing import Any, cast

from sqlalchemy import select

from app.database import utils
from app.database.repository import AlchemyRepository
from app.database.utils import validate
from app.users.models import UserOrm
from app.users.schemas import UserRead


class UserRepository(AlchemyRepository):
    async def create(self, **kwargs: Any) -> UserRead:
        user = UserOrm(**kwargs)
        self.session.add(user)
        await self.session.flush()
        return validate(user, UserRead)

    async def get(self, user_id: str) -> UserRead | None:
        user = await self.session.get(UserOrm, user_id)
        return validate(user, UserRead)

    async def get_by_email(self, email: str) -> UserRead | None:
        stmt = select(UserOrm).where(UserOrm.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar()
        return validate(user, UserRead)

    async def update(self, user_id: str, data: dict[str, Any]) -> UserRead:
        user = cast(UserOrm, await self.session.get_one(UserOrm, user_id))
        utils.update_attrs(user, data)
        await self.session.flush()
        return validate(user, UserRead)

    async def delete(self, user_id: str) -> UserRead:
        user = cast(UserOrm, await self.session.get_one(UserOrm, user_id))
        await self.session.delete(user)
        await self.session.flush()
        return validate(user, UserRead)
