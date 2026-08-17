"""Reranking.

Dev mode: a cheap lexical+score blend that simulates a cross-encoder stage.
Production: point ``Reranker`` at a cross-encoder or a second-pass LLM judge.
"""

from __future__ import annotations

import re

_PUNCT = re.compile(r"[.,;:!?()\"']")


def _tokens(text: str) -> set[str]:
    return {t for t in _PUNCT.sub(" ", text.lower()).split()}


class Reranker:
    """Reranks a list of retrieval result dicts in place."""

    def __init__(self, enabled: bool = False, top_k: int = 8) -> None:
        self.enabled = enabled
        self.top_k = top_k

    def _blended(self, query: str, result: dict) -> float:
        q = _tokens(query)
        text = result.get("text", "")
        overlap = len(q & _tokens(text)) / max(1, len(q))
        score = float(result.get("score", 0.0))
        return 0.8 * score + 0.2 * overlap

    def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: int | None = None,
    ) -> list[dict]:
        if not results:
            return results
        k = top_k or self.top_k
        if self.enabled:
            scored = sorted(
                results,
                key=lambda r: self._blended(query, r),
                reverse=True,
            )
        else:
            scored = sorted(results, key=lambda r: float(r.get("score", 0)), reverse=True)
        return scored[:k]


__all__ = ["Reranker"]