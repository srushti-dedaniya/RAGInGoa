"""End-to-end voice → Sarvam → RAG endpoint."""
from fastapi import APIRouter, HTTPException, Request, UploadFile

from ..config.constants import MAX_AUDIO_BYTES, SUPPORTED_AUDIO_TYPES, SUPPORTED_STT_LANGUAGES
from ..models.response import QueryResponse

router = APIRouter(tags=["voice"])

@router.post("/rag/voice", response_model=QueryResponse)
async def voice_query(
    request: Request, file: UploadFile, top_k: int | None = None,
    language_code: str | None = None,
) -> QueryResponse:
    content_type = (file.content_type or "").split(";", 1)[0].strip().lower()
    if content_type and content_type not in SUPPORTED_AUDIO_TYPES:
        raise HTTPException(415, f"unsupported audio type: {file.content_type}")
    if language_code and language_code not in SUPPORTED_STT_LANGUAGES:
        raise HTTPException(400, "unsupported language; use en-IN, hi-IN, or mr-IN")
    data = await file.read(MAX_AUDIO_BYTES + 1)
    if not data:
        raise HTTPException(400, "empty audio upload")
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "audio file too large")
    return QueryResponse(**request.app.state.services.audio_query(
        data, file.filename or "audio.webm", top_k,
        language_code=language_code, content_type=content_type or None,
    ))

__all__ = ["router"]
