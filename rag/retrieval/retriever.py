"""Retriever — the public retrieval entry point."""

from __future__ import annotations

import time

from rag.retrieval.retrieval_config import RetrievalConfig
from rag.retrieval.reranker import Reranker


class Retriever:
    """Embeds a query, searches the index and (optionally) reranks."""

    def __init__(self, embedder, index, config: RetrievalConfig | None = None) -> None:
        self.embedder = embedder
        self.index = index
        self.config = config or RetrievalConfig()
        self.reranker = Reranker(
            enabled=self.config.rerank,
            top_k=self.config.rerank_top_k,
        )

    def is_ready(self) -> bool:
        return self.index is not None and self.index.size() > 0

    def _results(self, query: str, top_k: int | None) -> list[dict]:
        k = top_k or self.config.top_k
        qvec = self.embedder.embed(query)
        hits = self.index.search(qvec, top_k=max(k, self.config.rerank_top_k)) if self.is_ready() else []
        results = [
            {
                "chunk_id": h.chunk_id,
                "text": h.text,
                "metadata": dict(h.metadata),
                "score": h.score,
                "score_type": h.score_type,
            }
            for h in hits
        ]
        return self.reranker.rerank(query, results, top_k=k)

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict]:
        """Return ``top_k`` result dicts ordered by score."""
        return self._results(query, top_k)

    def retrieve_with_details(self, query: str, top_k: int | None = None) -> dict:
        """Return results plus latency and engine metadata."""
        started = time.perf_counter()
        results = self._results(query, top_k)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "query": query,
            "engine": f"dev-index/{self.index.model_name}" if self.is_ready() else "empty",
            "index_size": self.index.size() if self.index else 0,
            "latency_ms": latency_ms,
            "top_k": len(results),
            "results": results,
        }


__all__ = ["Retriever"]