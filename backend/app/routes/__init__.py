"""API routes."""

from fastapi import APIRouter

from . import query, transcribe, health, benchmark, voice

api_router = APIRouter()
api_router.include_router(query.router)
api_router.include_router(transcribe.router)
api_router.include_router(health.router)
api_router.include_router(benchmark.router)
api_router.include_router(voice.router)

__all__ = ["api_router"]
