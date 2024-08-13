from sqlalchemy import select

from app.db.repository import AlchemyGenericRepository
from app.db.utils import validate
from app.users.models import UserOrm
from app.users.schemas import UserRead


class UserRepository(AlchemyGenericRepository[UserOrm, UserRead]):
    model_type = UserOrm
    schema_type = UserRead

    async def get_by_email(self, email: str) -> UserRead | None:
        stmt = select(UserOrm).where(UserOrm.email == email)  # noqa
        result = await self.session.execute(stmt)
        user = result.scalar()
        return validate(user, UserRead)
