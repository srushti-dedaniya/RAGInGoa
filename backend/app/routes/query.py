"""Query routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ..models.request import QueryRequest
from ..models.response import QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query(request: Request, payload: QueryRequest) -> QueryResponse:
    services = request.app.state.services
    try:
        data = services.query(payload.query, top_k=payload.top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"query pipeline failed: {exc}") from exc
    return QueryResponse(**data)


@router.get("/ping")
async def query_ping() -> dict:
    return {"ok": True, "service": "query"}


__all__ = ["router"]