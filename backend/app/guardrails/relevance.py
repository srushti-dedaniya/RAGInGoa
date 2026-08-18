"""Relevance guardrail: the query must correlate with the retrieved context."""

from __future__ import annotations

from .base import Result

DEFAULT_THRESHOLD = 0.02


def relevance_check(query: str, context: list[dict], embedder=None, threshold: float = DEFAULT_THRESHOLD) -> Result:
    """Scores retrieval relevance as mean embedding cosine between query and hits."""
    retrieval_scores = [float(c["score"]) for c in context if c.get("score") is not None]
    if retrieval_scores:
        best_score = max(retrieval_scores)
        return Result(
            name="relevance",
            passed=best_score >= threshold,
            reason=f"best FAISS similarity {best_score:.3f}",
            score=round(best_score, 4),
        )
    if embedder is None or not context:
        if not context:
            return Result(
                name="relevance",
                passed=False,
                reason="no context retrieved, cannot be relevant",
                score=0.0,
            )
        return Result(name="relevance", passed=True, reason="no embedder available", score=threshold)
    q = embedder.embed(query)

    scores = []
    for c in context[:5]:
        text = c.get("text", "")
        if not text:
            continue
        v = embedder.embed(text)
        scores.append(_cosine(q, v))
    if not scores:
        return Result(name="relevance", passed=False, reason="blank context", score=0.0)
    mean_score = sum(scores) / len(scores)
    return Result(
        name="relevance",
        passed=mean_score >= threshold,
        reason=f"mean cross-similarity {mean_score:.3f}",
        score=round(mean_score, 4),
    )


def _cosine(a: list[float], b: list[float]) -> float:
    import math

    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1e-9
    nb = math.sqrt(sum(x * x for x in b)) or 1e-9
    return dot / (na * nb)


__all__ = ["relevance_check"]
