from fastapi.testclient import TestClient

from app.main import app
from app.services.tts_service import TTSError


def test_tts_returns_backend_audio(monkeypatch):
    with TestClient(app) as client:
        monkeypatch.setattr(app.state.services, "synthesize", lambda text, language: b"RIFFaudio")
        response = client.post("/api/tts", json={"text": "Hello", "language_code": "en-IN"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.content == b"RIFFaudio"


def test_tts_rejects_unsupported_language():
    with TestClient(app) as client:
        response = client.post("/api/tts", json={"text": "Hello", "language_code": "kok-IN"})
    assert response.status_code == 422


def test_tts_returns_useful_provider_error(monkeypatch):
    with TestClient(app) as client:
        def fail(*_args):
            raise TTSError("Sarvam text-to-speech is rate limited. Please try again shortly.")

        monkeypatch.setattr(app.state.services, "synthesize", fail)
        response = client.post("/api/tts", json={"text": "Hello", "language_code": "en-IN"})
    assert response.status_code == 502
    assert "rate limited" in response.json()["detail"]
