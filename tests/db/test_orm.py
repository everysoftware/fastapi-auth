import pytest

from app.core import UOW
from app.skeleton.orm import TestUser as User


@pytest.mark.asyncio
async def test_create(uow: UOW):
    """Test create."""
    user = User(name="Alice", age=18)
    uow.session.add(user)
    await uow.session.commit()

    assert user.name == "Alice"
    assert user.age == 18

    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None
