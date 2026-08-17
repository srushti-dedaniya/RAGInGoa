"""Guardrail pipeline: safety → relevance → grounding → refusal."""

from __future__ import annotations

from .base import Result
from .safety import safety_check
from .relevance import relevance_check
from .grounding import grounding_check
from .refusal import refusal_check


def run_all(
    query: str,
    context: list[dict],
    answer: str,
    embedder=None,
    threshold: float = 0.02,
) -> list[Result]:
    """Run every guardrail against a completed query turn."""
    return [
        safety_check(query),
        relevance_check(query, context, embedder=embedder, threshold=threshold),
        grounding_check(answer, context),
        refusal_check(query),
    ]


def summarize(results: list[Result]) -> dict:
    checks = [r.as_dict() for r in results]
    return {"passed": all(r.passed for r in results), "checks": checks}


__all__ = ["Result", "run_all", "summarize"]