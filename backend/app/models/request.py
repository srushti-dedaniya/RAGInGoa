"""Models for incoming requests."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)
    stream: bool = False
    language_code: Literal["en-IN", "hi-IN", "mr-IN"] = "en-IN"


class BenchmarkRequest(BaseModel):
    queries: list[str] | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)


__all__ = ["QueryRequest", "BenchmarkRequest"]
