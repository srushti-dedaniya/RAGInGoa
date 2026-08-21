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
        self._last_profile: dict[str, float] = {}

    def is_ready(self) -> bool:
        return self.index is not None and self.index.size() > 0

    def _results(
        self, query: str, top_k: int | None, language_code: str = "en-IN"
    ) -> list[dict]:
        k = top_k or self.config.top_k
        embed_started = time.perf_counter()
        qvec = self.embedder.embed(query)
        embedding_ms = (time.perf_counter() - embed_started) * 1000
        candidate_k = min(self.index.size(), max(k * 8, self.config.rerank_top_k))
        search_started = time.perf_counter()
        hits = self.index.search(qvec, top_k=candidate_k) if self.is_ready() else []
        vector_search_ms = (time.perf_counter() - search_started) * 1000
        results = [
            {
                "chunk_id": h.chunk_id,
                "text": h.text,
                "metadata": dict(h.metadata),
                "score": h.score,
                "score_type": h.score_type,
            }
            for h in hits
            if self._language_matches(h.metadata, language_code)
        ]
        # MSMARCO-XI includes the originating query in both Hindi and English.
        # A cheap metadata-intent pass fixes exact/cross-script matches that the
        # English-centric MiniLM model can otherwise miss, while FAISS remains
        # the semantic candidate source.
        by_id = {item["chunk_id"]: item for item in results}
        lexical_started = time.perf_counter()
        for item in self._metadata_matches(query, language_code):
            current = by_id.get(item["chunk_id"])
            if current is None or item["score"] > current["score"]:
                by_id[item["chunk_id"]] = item
        results = sorted(by_id.values(), key=lambda item: item["score"], reverse=True)
        lexical_ms = (time.perf_counter() - lexical_started) * 1000
        rerank_started = time.perf_counter()
        ranked = self.reranker.rerank(query, results, top_k=k)
        self._last_profile = {
            "embedding": round(embedding_ms, 2),
            "vector_search": round(vector_search_ms, 2),
            "metadata_filter": round(lexical_ms, 2),
            "reranking": round((time.perf_counter() - rerank_started) * 1000, 2),
        }
        return ranked

    @staticmethod
    def _language_matches(metadata: dict, language_code: str) -> bool:
        language = str(metadata.get("language", "")).lower()
        if language_code == "hi-IN":
            return language == "hi"
        if language_code == "mr-IN":
            return language == "mr"
        # Every XI target record retains its aligned original English passage.
        # Native English/sample documents remain valid for test and custom indexes.
        return language in {"", "en", "eng", "english"} or bool(metadata.get("english_passage"))

    @staticmethod
    def _terms(text: str) -> set[str]:
        stop = {"the", "a", "an", "is", "are", "what", "when", "how", "to", "of", "for",
                "क्या", "है", "के", "की", "का", "में", "काय", "आहे", "चा", "ची", "चे"}
        return {token for token in re.findall(r"[^\W_]+", text.lower(), re.UNICODE)
                if len(token) > 1 and token not in stop}

    def _metadata_matches(self, query: str, language_code: str) -> list[dict]:
        query_terms = self._terms(query)
        if not query_terms:
            return []
        matches = []
        for pos, (meta, intent_terms) in enumerate(zip(self.index.meta, self._intent_terms)):
            if not self._language_matches(meta, language_code):
                continue
            overlap = len(query_terms & intent_terms) / len(query_terms)
            if overlap < 0.5:
                continue
            matches.append({
                "chunk_id": self.index.ids[pos], "text": self.index.texts[pos],
                "metadata": dict(meta), "score": overlap, "score_type": "hybrid",
            })
        return matches

    def retrieve(
        self, query: str, top_k: int | None = None, language_code: str = "en-IN"
    ) -> list[dict]:
        """Return ``top_k`` result dicts ordered by score."""
        return self._results(query, top_k, language_code)

    def retrieve_with_details(
        self, query: str, top_k: int | None = None, language_code: str = "en-IN"
    ) -> dict:
        """Return results plus latency and engine metadata."""
        started = time.perf_counter()
        results = self._results(query, top_k, language_code)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "query": query,
            "engine": f"dev-index/{self.index.model_name}" if self.is_ready() else "empty",
            "index_size": self.index.size() if self.index else 0,
            "latency_ms": latency_ms,
            "top_k": len(results),
            "results": results,
            "profile": dict(self._last_profile),
        }


__all__ = ["Retriever"]
