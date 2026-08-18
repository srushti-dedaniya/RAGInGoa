"""End-to-end pipeline test through the real HTTP app."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_full_voice_turn(client):
    transcription = client.post(
        "/api/transcribe",
        files={"file": ("q.wav", b"\x00" * 512, "audio/wav")},
    ).json()
    assert transcription["transcript"]

    response = client.post("/api/query", json={"query": transcription["transcript"]})
    assert response.status_code == 200
    body = response.json()

    assert body["answer"]
    assert len(body["sources"]) >= 1
    assert body["engine"]["stt"] in {"dev", "sarvam"}
    assert body["latency_breakdown"]["total"] > 0
    assert body["guardrails"]["passed"] is True


def test_benchmark_round_trip(client):
    response = client.post("/api/benchmark", json={"queries": ["best beach in Goa", "what to eat"]})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["summary"]["queries"] == 2
    assert body["report"]["latency"]["retrieve"]["p50_ms"] >= 0

    latest = client.get("/api/benchmark").json()
    assert latest["success"] is True
