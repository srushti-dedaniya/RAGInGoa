"""Transcription routes (multipart audio upload)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, UploadFile

from ..config.constants import MAX_AUDIO_BYTES, SUPPORTED_AUDIO_TYPES
from ..models.response import TranscriptResponse

router = APIRouter(prefix="/transcribe", tags=["transcribe"])


@router.post("", response_model=TranscriptResponse)
async def transcribe(request: Request, file: UploadFile) -> TranscriptResponse:
    if file.content_type and file.content_type not in SUPPORTED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail=f"unsupported audio type: {file.content_type}")
    data = await file.read()
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="audio file too large")
    if not data:
        raise HTTPException(status_code=400, detail="empty audio upload")
    services = request.app.state.services
    result = services.transcribe(data, file.filename or "audio.webm")
    return TranscriptResponse(**result)


__all__ = ["router"]