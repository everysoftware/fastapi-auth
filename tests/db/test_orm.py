from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import UserOrm

faker = Faker()
user_info = {"email": faker.email(), "hashed_password": faker.password()}


async def test_add(session: AsyncSession) -> None:
    user = UserOrm(**user_info)
    session.add(user)
    await session.commit()

    assert user.id is not None
    assert user.email == user_info["email"]
    assert user.hashed_password == user_info["hashed_password"]
    assert user.created_at is not None
    assert user.updated_at is not None
