"""Retriever — the public retrieval entry point."""

from __future__ import annotations

import re
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
        self._intent_terms = [
            self._terms(f"{meta.get('query', '')} {meta.get('english_query', '')}")
            for meta in self.index.meta
        ]

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
        # MSMARCO-XI includes the originating query in both Hindi and English.
        # A cheap metadata-intent pass fixes exact/cross-script matches that the
        # English-centric MiniLM model can otherwise miss, while FAISS remains
        # the semantic candidate source.
        by_id = {item["chunk_id"]: item for item in results}
        for item in self._metadata_matches(query):
            current = by_id.get(item["chunk_id"])
            if current is None or item["score"] > current["score"]:
                by_id[item["chunk_id"]] = item
        results = sorted(by_id.values(), key=lambda item: item["score"], reverse=True)
        return self.reranker.rerank(query, results, top_k=k)

    @staticmethod
    def _terms(text: str) -> set[str]:
        stop = {"the", "a", "an", "is", "are", "what", "when", "how", "to", "of", "for",
                "क्या", "है", "के", "की", "का", "में", "काय", "आहे", "चा", "ची", "चे"}
        return {token for token in re.findall(r"[^\W_]+", text.lower(), re.UNICODE)
                if len(token) > 1 and token not in stop}

    def _metadata_matches(self, query: str) -> list[dict]:
        query_terms = self._terms(query)
        if not query_terms:
            return []
        matches = []
        for pos, (meta, intent_terms) in enumerate(zip(self.index.meta, self._intent_terms)):
            overlap = len(query_terms & intent_terms) / len(query_terms)
            if overlap < 0.5:
                continue
            matches.append({
                "chunk_id": self.index.ids[pos], "text": self.index.texts[pos],
                "metadata": dict(meta), "score": overlap, "score_type": "hybrid",
            })
        return matches

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
