"""Transcription routes (multipart audio upload)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, UploadFile

from ..config.constants import MAX_AUDIO_BYTES, SUPPORTED_AUDIO_TYPES, SUPPORTED_STT_LANGUAGES
from ..models.response import TranscriptResponse

router = APIRouter(prefix="/transcribe", tags=["transcribe"])


@router.post("", response_model=TranscriptResponse)
async def transcribe(
    request: Request, file: UploadFile, language_code: str | None = None,
) -> TranscriptResponse:
    content_type = (file.content_type or "").split(";", 1)[0].strip().lower()
    if content_type and content_type not in SUPPORTED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail=f"unsupported audio type: {file.content_type}")
    if language_code and language_code not in SUPPORTED_STT_LANGUAGES:
        raise HTTPException(400, "unsupported language; use en-IN, hi-IN, or mr-IN")
    data = await file.read()
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="audio file too large")
    if not data:
        raise HTTPException(status_code=400, detail="empty audio upload")
    services = request.app.state.services
    result = services.transcribe(
        data, file.filename or "audio.webm",
        language_code=language_code, content_type=content_type or None,
    )
    return TranscriptResponse(**result)


__all__ = ["router"]
