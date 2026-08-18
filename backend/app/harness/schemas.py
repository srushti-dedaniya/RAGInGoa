"""Internal pipeline data structures (dataclasses, not API models)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StageResult:
    name: str
    ok: bool
    data: Any = None
    latency_ms: float = 0.0
    error: str | None = None


@dataclass
class PipelineResult:
    query: str
    answer: str = ""
    sources: list[dict] = field(default_factory=list)
    grounded: bool = False
    guardrails: list[dict] = field(default_factory=list)
    latency_breakdown: dict[str, float] = field(default_factory=dict)
    engine: dict[str, str] = field(default_factory=dict)
    intermediate: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    stages: list[StageResult] = field(default_factory=list)


__all__ = ["StageResult", "PipelineResult"]
