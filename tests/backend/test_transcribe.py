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
    assert body["engine"] == "test-stt"
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


@pytest.mark.parametrize("language_code", ["en-IN", "hi-IN", "mr-IN"])
def test_voice_accepts_browser_webm_codec_and_language(client, language_code):
    response = client.post(
        f"/api/rag/voice?language_code={language_code}",
        files={"file": ("recording.webm", b"\x00" * 512, "audio/webm;codecs=opus")},
    )
    assert response.status_code == 200
    assert response.json()["query"]


def test_voice_rejects_unsupported_language(client):
    response = client.post(
        "/api/rag/voice?language_code=fr-FR",
        files={"file": ("recording.webm", b"\x00" * 512, "audio/webm")},
    )
    assert response.status_code == 400
