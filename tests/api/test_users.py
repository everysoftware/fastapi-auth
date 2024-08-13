from starlette.testclient import TestClient

from app.users.schemas import UserRead


def test_me(
    client: TestClient, existing_user: UserRead, user_headers: dict[str, str]
) -> None:
    response = client.get("/users/me", headers=user_headers)
    print(response.json())
    assert response.status_code == 200
    user = UserRead.model_validate(response.json())
    assert user == existing_user
