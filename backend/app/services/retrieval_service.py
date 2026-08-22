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
        self._retrievers: dict[str, Retriever] = {}

    @property
    def retriever(self) -> Retriever:
        return self._get_retriever("en-IN")

    def _get_retriever(self, language_code: str) -> Retriever:
        language_code = language_code if language_code in {"en-IN", "hi-IN", "mr-IN"} else "en-IN"
        if language_code not in self._retrievers:
            self._retrievers[language_code] = self._build(language_code)
        return self._retrievers[language_code]

    def _build(self, language_code: str) -> Retriever:
        index_path = self.settings.index_path_for(language_code)
        index = load_index(index_path, model_name=self.embedder.model_name())
        if index is None or index.size() == 0:
            if self.settings.REQUIRE_INDEX:
                raise RuntimeError(
                    f"persistent {language_code} index missing at {index_path}; run scripts/build_index.py"
                )
            index = self._build_from_samples(index_path)
        return Retriever(self.embedder, index, self.config)

    def _build_from_samples(self, index_path):
        logger.info("no index on disk; building dev index from sample corpus")
        samples = self.settings.sample_data_path
        docs = read_data(samples)
        chunks = ChunkManager(
            self.settings.CHUNK_STRATEGY,
            {"size": self.settings.CHUNK_SIZE, "overlap": self.settings.CHUNK_OVERLAP},
        ).split(docs)
        return build_index(self.embedder, chunks, index_path)

    def is_ready(self) -> bool:
        return all(self._get_retriever(code).is_ready() for code in ("en-IN", "hi-IN", "mr-IN"))

    def index_size(self) -> int:
        return sum(self._get_retriever(code).index.size() for code in ("en-IN", "hi-IN", "mr-IN"))

    def retrieve(
        self, query: str, top_k: int | None = None, language_code: str = "en-IN"
    ) -> list[dict]:
        return self._get_retriever(language_code).retrieve(
            query, top_k=top_k, language_code=language_code
        )

    def details(
        self, query: str, top_k: int | None = None, language_code: str = "en-IN"
    ) -> dict:
        details = self._get_retriever(language_code).retrieve_with_details(
            query, top_k=top_k, language_code=language_code
        )
        details["engine"] = "FAISS"
        details["language_code"] = language_code
        details["index_path"] = str(self.settings.index_path_for(language_code))
        return details


__all__ = ["RetrievalService"]
