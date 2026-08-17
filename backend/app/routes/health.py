"""Health / status routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from ..models.response import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    services = request.app.state.services
    return HealthResponse(**services.health())


__all__ = ["router"]