"""Query routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from ..models.request import QueryRequest
from ..models.response import QueryResponse

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
@router.post("/rag/query", response_model=QueryResponse)
async def query(request: Request, payload: QueryRequest) -> QueryResponse:
    services = request.app.state.services
    data = services.query(
        payload.query, top_k=payload.top_k, language_code=payload.language_code
    )
    return QueryResponse(**data)


@router.get("/query/ping")
async def query_ping() -> dict:
    return {"ok": True, "service": "query"}


__all__ = ["router"]
