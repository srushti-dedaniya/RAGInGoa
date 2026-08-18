"""Safety guardrail: block harmful-intent queries with a lightweight blocklist."""

from __future__ import annotations

from .base import Result

_BLOCKLIST = {
    "chain instructions",
    "ignore previous",
    "ignore all previous",
    "disregard your",
    "reveal your system",
    "system prompt",
    "forget your instructions",
    "act as if",
    "dansking",
    "harm me",
    "injure",
    "how to make a bomb",
    "bypass",
}


def safety_check(query: str) -> Result:
    lowered = query.lower().strip()
    for token in _BLOCKLIST:
        if token in lowered:
            return Result(
                name="safety",
                passed=False,
                reason=f"query matched blocked pattern: '{token}'",
                score=0.0,
            )
    return Result(name="safety", passed=True, reason="no unsafe patterns detected", score=1.0)


__all__ = ["safety_check"]
