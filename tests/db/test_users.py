import pytest

from app.database.uow import UOW


@pytest.mark.asyncio
async def test_create(uow: UOW):
    user = await uow.users.create(
        email="user@example.com", hashed_password="test"
    )
    assert user.id is not None
    assert user.email == "user@example.com"
    assert user.hashed_password == "test"
    assert user.created_at is not None
    assert user.updated_at is not None
