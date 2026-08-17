"""Grounding guardrail: the answer must cite retrieved sources."""

from __future__ import annotations

from .base import Result


def grounding_check(answer: str, context: list[dict]) -> Result:
    """Passes when the answer references ≥1 source key found in the context."""
    if not context:
        return Result(
            name="grounding",
            passed=False,
            reason="no context to ground against",
            score=0.0,
        )
    answered = answer.lower()
    cited: list[str] = []
    for c in context:
        meta = c.get("metadata", {})
        keys = [meta.get("title"), meta.get("source"), c.get("chunk_id")]
        for key in keys:
            if key and str(key).lower() in answered:
                cited.append(str(key))
                break
    score = min(1.0, len(cited) / max(1, len(context)))
    passed = len(cited) >= 1
    reason = (
        f"answer cites {len(cited)} source(s)" if passed
        else "answer does not cite any retrieved source"
    )
    return Result(
        name="grounding",
        passed=passed,
        reason=reason,
        score=round(score, 4),
    )


__all__ = ["grounding_check"]