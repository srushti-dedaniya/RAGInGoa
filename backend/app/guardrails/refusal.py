"""Refusal guardrail: decline prompt-injection style instructions."""

from __future__ import annotations

from .base import Result

_INJECTION_HINTS = (
    "ignore all previous instructions",
    "ignore the instructions",
    "forget everything",
    "you are now",
    "system prompt",
    "developer mode",
    "pretend you are",
    "answer without context",
    "do not use sources",
    "disable guardrails",
)


def refusal_check(query: str) -> Result:
    lowered = query.lower().strip()
    for hint in _INJECTION_HINTS:
        if hint in lowered:
            return Result(
                name="refusal",
                passed=False,
                reason=f"possible prompt-injection pattern: '{hint}'",
                score=0.0,
            )
    return Result(name="refusal", passed=True, reason="no injection patterns detected", score=1.0)


__all__ = ["refusal_check"]