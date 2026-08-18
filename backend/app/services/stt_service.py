"""Sarvam speech-to-text service with bounded retries and timeouts."""
from __future__ import annotations

import io
import time
import httpx

from ..config.settings import Settings


class STTError(RuntimeError):
    pass


class STTService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.router = settings.STT_ROUTER.lower()
        self.client = httpx.Client(timeout=settings.EXTERNAL_TIMEOUT_SECONDS)

    def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        language_code: str | None = None,
        content_type: str | None = None,
    ) -> dict:
        started = time.perf_counter()
        if self.router == "dev":
            from ..config.constants import DEV_TRANSCRIPT
            payload = {"transcript": DEV_TRANSCRIPT, "language": "en-IN", "engine": "test-stt"}
        elif self.router == "sarvam":
            payload = self._sarvam(audio_bytes, filename, language_code, content_type)
        else:
            raise STTError(f"unsupported STT_ROUTER '{self.router}'; use sarvam")
        payload.update({"success": True, "processing_time_ms": round((time.perf_counter()-started)*1000, 2)})
        payload["latency_ms"] = payload["processing_time_ms"]
        return payload

    def _sarvam(
        self,
        audio_bytes: bytes,
        filename: str,
        language_code: str | None,
        content_type: str | None,
    ) -> dict:
        if not self.settings.SARVAM_API_KEY:
            raise STTError("Sarvam STT is not configured")
        last_error: Exception | None = None
        failure_message = "Sarvam transcription failed. Please try recording again."
        retryable = {429, 500, 502, 503, 504}
        for attempt in range(self.settings.EXTERNAL_MAX_RETRIES + 1):
            try:
                response = self.client.post(
                    self.settings.SARVAM_STT_URL,
                    headers={"api-subscription-key": self.settings.SARVAM_API_KEY},
                    files={"file": (filename, io.BytesIO(audio_bytes), content_type or "application/octet-stream")},
                    data={"model": self.settings.SARVAM_STT_MODEL, "mode": "transcribe",
                          "language_code": language_code or self.settings.SARVAM_LANGUAGE_CODE},
                )
                if response.status_code in retryable and attempt < self.settings.EXTERNAL_MAX_RETRIES:
                    continue
                if response.status_code in {401, 403}:
                    raise STTError("Sarvam authentication failed. Check the backend API key configuration.")
                if response.status_code == 413:
                    raise STTError("The recording is too large for Sarvam. Record a shorter clip.")
                if response.status_code in {400, 422}:
                    raise STTError("Sarvam could not decode the recording. Use a supported browser and record under 30 seconds.")
                if response.status_code == 429:
                    raise STTError("Sarvam is rate limited. Wait briefly and try again.")
                response.raise_for_status()
                data = response.json()
                transcript = str(data.get("transcript") or "").strip()
                if not transcript:
                    raise STTError("Sarvam returned an empty transcript")
                return {"transcript": transcript, "language": data.get("language_code"),
                        "request_id": data.get("request_id"), "engine": self.settings.SARVAM_STT_MODEL}
            except STTError:
                raise
            except httpx.TimeoutException as exc:
                last_error = exc
                failure_message = "Sarvam timed out. Check the connection and try again."
                if attempt >= self.settings.EXTERNAL_MAX_RETRIES:
                    break
            except httpx.NetworkError as exc:
                last_error = exc
                failure_message = "Sarvam is unreachable from the backend. Check the network and try again."
                if attempt >= self.settings.EXTERNAL_MAX_RETRIES:
                    break
            except (httpx.HTTPStatusError, ValueError) as exc:
                last_error = exc
                if attempt >= self.settings.EXTERNAL_MAX_RETRIES:
                    break
        raise STTError(failure_message) from last_error


__all__ = ["STTService", "STTError"]
