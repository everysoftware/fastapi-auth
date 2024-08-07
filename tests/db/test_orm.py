from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import UserOrm


async def test_add(session: AsyncSession) -> None:
    user = UserOrm(email="user@example.com", hashed_password="test")
    session.add(user)
    await session.commit()

    assert user.id is not None
    assert user.email == "user@example.com"
    assert user.hashed_password == "test"
    assert user.created_at is not None
    assert user.updated_at is not None
