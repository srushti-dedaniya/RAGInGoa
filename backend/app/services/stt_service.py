"""Speech-to-text service (dev + whisper routers)."""

from __future__ import annotations

import logging
import time

from ..config.constants import DEV_TRANSCRIPT
from ..config.settings import Settings

logger = logging.getLogger(__name__)


class STTService:
    """Transcribes audio bytes. Dev router returns a canned demo transcript."""

    def __init__(self, settings: Settings) -> None:
        self.router = settings.STT_ROUTER.lower()

    def transcribe(self, audio_bytes: bytes, filename: str = "") -> dict:
        started = time.perf_counter()
        if self.router == "whisper":
            result = self._whisper(audio_bytes, filename)
        else:
            result = {"transcript": DEV_TRANSCRIPT, "engine": "dev-stt"}
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        result["latency_ms"] = latency_ms
        result["confidence"] = result.get("confidence", 1.0)
        result["input_bytes"] = len(audio_bytes)
        return result

    def _whisper(self, audio_bytes: bytes, filename: str) -> dict:
        from openai import OpenAI  # optional dep

        key = self._settings_key()
        if not key:
            logger.warning("STT_ROUTER=whisper but no OPENAI_API_KEY; falling back to dev STT")
            return {"transcript": DEV_TRANSCRIPT, "engine": "dev-stt"}
        client = OpenAI(api_key=key)
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename or "audio.webm", audio_bytes),
        )
        return {
            "transcript": transcription.text,
            "confidence": 1.0,
            "engine": "openai-whisper-1",
        }

    def _settings_key(self) -> str:
        from ..config.settings import get_settings

        return get_settings().OPENAI_API_KEY


__all__ = ["STTService"]