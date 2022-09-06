from fastapi.testclient import TestClient


def test_healthz(client: TestClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    response = client.get("/is-ready")
    assert response.status_code == 200
