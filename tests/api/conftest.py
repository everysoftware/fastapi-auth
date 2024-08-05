import pytest
from starlette.testclient import TestClient

from app import app
from app.users.schemas import UserCreate, UserRead

user_create = UserCreate(email="user@example.com", password="test")


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client: TestClient):
    response = client.post("/auth/register", json=user_create.model_dump())
    assert response.status_code == 201
    response_json = response.json()
    response_json["hashed_password"] = ""
    user = UserRead.model_validate(response_json)
    yield user
    response = client.delete("/users/me")
    assert response.status_code == 204


@pytest.fixture
def auth_cookies(client: TestClient, registered_user):
    response = client.post(
        "/auth/login",
        data={"username": user_create.email, "password": user_create.password},
    )
    return response.cookies
