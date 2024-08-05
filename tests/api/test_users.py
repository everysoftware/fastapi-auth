from typing import Any

from starlette.testclient import TestClient


def test_me(client: TestClient, auth_cookies: dict[str, Any]):
    response = client.get("/users/me", cookies=auth_cookies)
    assert response.status_code == 200
