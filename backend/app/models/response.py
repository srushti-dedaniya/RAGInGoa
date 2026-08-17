"""Response models for the API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Source(BaseModel):
    text: str
    chunk_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float = 0.0
    score_type: str = "cosine"


class GuardrailCheck(BaseModel):
    name: str
    passed: bool
    reason: str = ""
    score: float = 0.0


class GuardrailSummary(BaseModel):
    passed: bool
    checks: list[GuardrailCheck] = Field(default_factory=list)


class LatencyBreakdown(BaseModel):
    stt: float = 0.0
    retrieval: float = 0.0
    generation: float = 0.0
    guardrails: float = 0.0
    total: float = 0.0


class EngineInfo(BaseModel):
    stt: str = "dev"
    llm: str = "dev"
    vector_db: str = "dev"
    embedding: str = ""


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[Source] = Field(default_factory=list)
    confidence: float = 0.0
    guardrails: GuardrailSummary | None = None
    latency_breakdown: LatencyBreakdown = Field(default_factory=LatencyBreakdown)
    engine: EngineInfo = Field(default_factory=EngineInfo)
    intermediate: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)


class TranscriptResponse(BaseModel):
    transcript: str
    confidence: float = 1.0
    engine: str = "dev"
    latency_ms: float = 0.0


class HealthResponse(BaseModel):
    service: str = "RAGInGoa"
    status: str = "ONLINE"
    version: str = "1.0.0"
    uptime_seconds: float = 0.0
    routers: dict[str, str] = Field(default_factory=dict)
    index_size: int = 0
    ready: bool = True


class BenchmarkResult(BaseModel):
    success: bool = True
    run_at: str = ""
    summary: dict[str, Any] = Field(default_factory=dict)
    report: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "Source",
    "GuardrailCheck",
    "GuardrailSummary",
    "LatencyBreakdown",
    "EngineInfo",
    "QueryResponse",
    "TranscriptResponse",
    "HealthResponse",
    "BenchmarkResult",
]