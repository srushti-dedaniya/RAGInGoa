"""Retrieval service — embeds the query and searches the vector index."""

from __future__ import annotations

import logging
import time

from rag.chunking.chunk_manager import ChunkManager
from rag.dataset.loader import read_data
from rag.embeddings.embedder import Embedder
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig
from rag.vector_db.index import build_index, load_index

from ..config.settings import Settings

logger = logging.getLogger(__name__)


class RetrievalService:
    """Lazy-built retriever over the dev numpy index (or a provided router)."""

    def __init__(self, settings: Settings, embedder: Embedder) -> None:
        self.settings = settings
        self.embedder = embedder
        self.config = RetrievalConfig(
            top_k=settings.TOP_K,
            score_threshold=settings.SCORE_THRESHOLD,
            rerank=settings.RERANK,
        )
        self._retriever: Retriever | None = None

    @property
    def retriever(self) -> Retriever:
        if self._retriever is None:
            self._retriever = self._build()
        return self._retriever

    def _build(self) -> Retriever:
        index = load_index(self.settings.index_path, model_name=self.embedder.model_name())
        if index is None or index.size() == 0:
            index = self._build_from_samples()
        return Retriever(self.embedder, index, self.config)

    def _build_from_samples(self):
        logger.info("no index on disk; building dev index from sample corpus")
        samples = self.settings.sample_data_path
        docs = read_data(samples)
        chunks = ChunkManager(
            self.settings.CHUNK_STRATEGY,
            {"size": self.settings.CHUNK_SIZE, "overlap": self.settings.CHUNK_OVERLAP},
        ).split(docs)
        return build_index(self.embedder, chunks, self.settings.index_path)

    def is_ready(self) -> bool:
        return self.retriever.is_ready()

    def index_size(self) -> int:
        return self.retriever.index.size() if self.retriever.index else 0

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict]:
        return self.retriever.retrieve(query, top_k=top_k)

    def details(self, query: str, top_k: int | None = None) -> dict:
        started = time.perf_counter()
        results = self.retrieve(query, top_k=top_k)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "query": query,
            "engine": f"dev/{self.embedder.model_name()}",
            "top_k": len(results),
            "latency_ms": latency_ms,
            "results": results,
        }


__all__ = ["RetrievalService"]