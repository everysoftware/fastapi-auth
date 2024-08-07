from typing import AsyncGenerator

import pytest
from httpx import Cookies
from starlette.testclient import TestClient

from app import app
from app.database.uow import UOW
from app.dependencies import get_uow
from app.users.schemas import UserCreate, UserRead
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
def user_cookies(client: TestClient, existing_user: UserRead) -> Cookies:
    response = client.post(
        "/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": user_create.email, "password": user_create.password},
    )
    assert response.status_code == 204
    assert "access_token" in response.cookies
    return response.cookies


@pytest.fixture
def user_headers(user_cookies: Cookies) -> dict[str, str]:
    return {"Authentication": f"Bearer {user_cookies["access_token"]}"}
