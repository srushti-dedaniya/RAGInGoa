"""Retrieval metrics."""

from __future__ import annotations


def precision_at_k(relevant: list[bool], k: int) -> float:
    """Precision over the first ``k`` retrieved items."""
    prefix = relevant[:k]
    if not prefix:
        return 0.0
    return sum(prefix) / len(prefix)


def recall_at_k(relevant: list[bool], k: int, total_relevant: int) -> float:
    """Recall over the first ``k`` retrieved items."""
    if total_relevant <= 0:
        return 0.0
    return sum(relevant[:k]) / total_relevant


def mrrt(relevant: list[bool]) -> float:
    """Mean reciprocal rank on a boolean relevance list."""
    for i, hit in enumerate(relevant, start=1):
        if hit:
            return 1.0 / i
    return 0.0


def hit_at_k(relevant: list[bool], k: int) -> bool:
    return any(relevant[:k])


__all__ = ["precision_at_k", "recall_at_k", "mrrt", "hit_at_k"]