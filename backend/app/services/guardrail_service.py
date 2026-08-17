"""Guardrail service — runs the four guardrails over a query turn."""

from __future__ import annotations

import time

from ..config.settings import Settings
from ..guardrails import run_all, summarize


class GuardrailService:
    """Evaluates safety, relevance, grounding and refusal for a turn."""

    def __init__(self, settings: Settings, embedder=None) -> None:
        self.settings = settings
        self.embedder = embedder
        self.threshold = settings.SCORE_THRESHOLD if settings.SCORE_THRESHOLD > 0 else 0.02

    def evaluate(self, query: str, context: list[dict], answer: str) -> dict:
        started = time.perf_counter()
        results = run_all(
            query,
            context,
            answer,
            embedder=self.embedder,
            threshold=self.threshold,
        )
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        summary = summarize(results)
        summary["latency_ms"] = latency_ms
        return summary


__all__ = ["GuardrailService"]