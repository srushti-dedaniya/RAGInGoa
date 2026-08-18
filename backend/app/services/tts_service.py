"""Server-side Sarvam Bulbul text-to-speech integration."""
from __future__ import annotations

import base64
import httpx

from ..config.constants import SUPPORTED_STT_LANGUAGES
from ..config.settings import Settings


class TTSError(RuntimeError):
    pass


class TTSService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = httpx.Client(timeout=settings.EXTERNAL_TIMEOUT_SECONDS)

    def synthesize(self, text: str, language_code: str) -> bytes:
        cleaned = text.strip()
        if not cleaned:
            raise TTSError("Text is required for speech synthesis.")
        if len(cleaned) > 2500:
            raise TTSError("The answer is too long to read aloud.")
        if language_code not in SUPPORTED_STT_LANGUAGES:
            raise TTSError("Unsupported language for speech synthesis.")
        if not self.settings.SARVAM_API_KEY:
            raise TTSError("Sarvam TTS is not configured on the backend.")

        try:
            response = self.client.post(
                self.settings.SARVAM_TTS_URL,
                headers={"api-subscription-key": self.settings.SARVAM_API_KEY},
                json={
                    "text": cleaned,
                    "language_code": language_code,
                    "model": self.settings.SARVAM_TTS_MODEL,
                    "speaker": self.settings.SARVAM_TTS_SPEAKER,
                    "pace": 1.0,
                    "temperature": 0.6,
                    "speech_sample_rate": 24000,
                },
            )
            if response.status_code in {401, 403}:
                raise TTSError("Sarvam authentication failed for text-to-speech.")
            if response.status_code == 429:
                raise TTSError("Sarvam text-to-speech is rate limited. Please try again shortly.")
            if response.status_code in {400, 422}:
                raise TTSError("Sarvam could not synthesize this answer.")
            response.raise_for_status()
            audios = response.json().get("audios") or []
            if not audios:
                raise TTSError("Sarvam returned no audio.")
            return base64.b64decode(audios[0], validate=True)
        except TTSError:
            raise
        except httpx.TimeoutException as exc:
            raise TTSError("Text-to-speech timed out. Please try again.") from exc
        except httpx.NetworkError as exc:
            raise TTSError("Sarvam text-to-speech is currently unreachable.") from exc
        except (httpx.HTTPStatusError, ValueError) as exc:
            raise TTSError("Text-to-speech failed. Please try again.") from exc


__all__ = ["TTSService", "TTSError"]
