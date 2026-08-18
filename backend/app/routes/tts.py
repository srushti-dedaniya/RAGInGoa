"""Text-to-speech route; credentials never leave the backend."""
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from ..services.tts_service import TTSError

router = APIRouter(tags=["tts"])


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2500)
    language_code: Literal["en-IN", "hi-IN", "mr-IN"] = "en-IN"


@router.post("/tts")
async def synthesize(request: Request, payload: TTSRequest) -> Response:
    try:
        audio = request.app.state.services.synthesize(payload.text, payload.language_code)
    except TTSError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return Response(
        content=audio,
        media_type="audio/wav",
        headers={"Cache-Control": "no-store"},
    )


__all__ = ["router"]
