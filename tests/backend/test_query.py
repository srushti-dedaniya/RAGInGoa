import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_query_returns_grounded_answer(client):
    response = client.post(
        "/api/query",
        json={"query": "When is the best time to visit Palolem?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["query"]
    assert body["answer"]
    assert body["sources"]
    assert body["confidence"] > 0
    assert body["guardrails"]["passed"] is True
    assert body["latency_breakdown"]["total"] >= 0


def test_query_rejects_empty(client):
    response = client.post("/api/query", json={"query": ""})
    assert response.status_code == 422


def test_query_honors_top_k(client):
    response = client.post("/api/query", json={"query": "best beach in Goa", "top_k": 2})
    assert response.status_code == 200
    assert len(response.json()["sources"]) <= 2