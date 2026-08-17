"""API routes."""

from fastapi import APIRouter

from . import query, transcribe, health, benchmark

api_router = APIRouter()
api_router.include_router(query.router)
api_router.include_router(transcribe.router)
api_router.include_router(health.router)
api_router.include_router(benchmark.router)

__all__ = ["api_router"]