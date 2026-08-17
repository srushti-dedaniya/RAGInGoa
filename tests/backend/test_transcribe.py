import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_transcribe_dev_router(client):
    response = client.post(
        "/api/transcribe",
        files={"file": ("demo.wav", b"\x00\x01\x02" * 100, "audio/wav")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["transcript"]
    assert body["engine"] == "dev-stt"
    assert body["latency_ms"] >= 0


def test_transcribe_rejects_empty(client):
    response = client.post(
        "/api/transcribe",
        files={"file": ("empty.wav", b"", "audio/wav")},
    )
    assert response.status_code == 400


def test_transcribe_rejects_unknown_type(client):
    response = client.post(
        "/api/transcribe",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 415