import pytest
from starlette.testclient import TestClient


# API tests come last
@pytest.mark.order(-1)
class TestHealthCheck:
    def test_hc(self, client: TestClient):
        response = client.get("/hc")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
