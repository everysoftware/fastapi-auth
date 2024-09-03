from typing import AsyncGenerator

import pytest
from starlette.testclient import TestClient

from app import app
from app.db.uow import UOW
from app.dependencies import get_uow
from app.users.schemas import UserCreate, UserRead, BearerToken
from tests.conftest import test_factory


async def get_test_uow() -> AsyncGenerator[UOW, None]:
    async with UOW(test_factory) as uow:
        yield uow


app.dependency_overrides[get_uow] = get_test_uow  # noqa
test_client = TestClient(app)


@pytest.fixture(scope="session")
def client() -> TestClient:
    return test_client


user_create = UserCreate(email="user@example.com", password="test")


@pytest.fixture
def existing_user(client: TestClient) -> UserRead:
    response = client.post("/auth/register", json=user_create.model_dump())
    assert response.status_code == 201
    response_json = response.json()
    user = UserRead.model_validate(response_json)

    assert user.id is not None
    assert user.email == user_create.email
    assert user.is_active
    assert not user.is_superuser
    assert not user.is_verified
    assert user.created_at is not None
    assert user.updated_at is not None

    return user


@pytest.fixture
def user_headers(
    client: TestClient, existing_user: UserRead
) -> dict[str, str]:
    response = client.post(
        "/auth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": user_create.email,
            "password": user_create.password,
        },
    )
    assert response.status_code == 200

    json = response.json()
    token = BearerToken.model_validate(json)

    return {"Authorization": f"Bearer {token.access_token}"}
