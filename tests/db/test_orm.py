import pytest

from app.core.uow import UOW
from app.testing import Waffle


@pytest.mark.asyncio
async def test_create(uow: UOW):
    """Test create."""
    waffle = Waffle(name="Bob", age=18)
    uow.session.add(waffle)
    await uow.session.commit()

    assert waffle.name == "Bob"
    assert waffle.age == 18

    assert waffle.id is not None
    assert waffle.created_at is not None
    assert waffle.updated_at is not None
