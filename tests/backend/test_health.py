import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "RAGInGoa"
    assert body["status"] in {"ONLINE", "DEGRADED"}
    assert body["ready"] is True
    assert body["index_size"] > 0


def test_root_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "RAGInGoa"