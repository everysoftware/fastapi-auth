from starlette.testclient import TestClient


def test_hc(client: TestClient) -> None:
    response = client.get("/api/v1/hc")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
