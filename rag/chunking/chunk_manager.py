"""Chunk manager — the public entry point for splitting documents."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from rag.dataset.cleaner import clean_text


@dataclass
class Chunk:
    """A retrievable unit of text."""

    text: str
    chunk_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    start_char: int = 0
    end_char: int = 0
    strategy: str = ""

    @property
    def tokens(self) -> int:
        return len(self.text.split())


class ChunkSplitter:
    """Base class for strategies. Subclasses implement ``split_text``."""

    name = "base"

    def __init__(self, size: int = 500, overlap: int = 0, **_: object) -> None:
        self.size = int(size)
        self.overlap = int(overlap)

    def split_text(self, text: str, doc_id: str, metadata: dict) -> list[Chunk]:
        raise NotImplementedError


class ChunkManager:
    """Selects and runs a chunking strategy over a corpus.

    ``strategy`` is one of ``fixed | sentence | semantic | metadata | hierarchical``. Config is
    a dict passed as kwargs to the strategy (``size``, ``overlap``, ...).
    """

    REGISTRY: dict[str, type[ChunkSplitter]] = {}

    def __init__(self, strategy: str = "sentence", config: dict | None = None) -> None:
        self.strategy_name = strategy
        self.config = config or {}
        self.splitter = self._build(strategy)

    @classmethod
    def register(cls, name: str) -> Any:
        def deco(splitter_cls: type[ChunkSplitter]) -> type[ChunkSplitter]:
            cls.REGISTRY[name] = splitter_cls
            return splitter_cls

        return deco

    def _build(self, strategy: str) -> ChunkSplitter:
        from rag.chunking.fixed_size import FixedSizeChunker
        from rag.chunking.sentence_based import SentenceChunker
        from rag.chunking.semantic import SemanticChunker
        from rag.chunking.metadata_aware import MetadataAwareChunker
        from rag.chunking.hierarchical import HierarchicalChunker

        table = {
            "fixed": FixedSizeChunker,
            "sentence": SentenceChunker,
            "semantic": SemanticChunker,
            "hierarchical": HierarchicalChunker,
        }
        if strategy in ("metadata", "metadata-aware"):
            inner = table[self.config.get("inner", "sentence")](**self.config)
            return MetadataAwareChunker(inner)
        if strategy not in table:
            raise ValueError(f"unknown chunking strategy: {strategy}")
        return table[strategy](**self.config)

    def split(self, documents: list[dict]) -> list[Chunk]:
        """Split ``[{content, metadata}]`` into ``Chunk`` objects."""
        chunks: list[Chunk] = []
        for i, doc in enumerate(documents):
            content = clean_text(doc.get("content"))
            if not content:
                continue
            meta = dict(doc.get("metadata") or {})
            doc_id = meta.get("id") or f"doc-{i:04d}"
            doc_chunks = self.splitter.split_text(content, str(doc_id), meta)
            for position, chunk in enumerate(doc_chunks):
                chunk.metadata.update({
                    "document_id": str(doc_id),
                    "chunk_id": chunk.chunk_id, "position": position,
                    "chunking_strategy": chunk.strategy or self.strategy_name,
                    "text_length": len(chunk.text),
                })
                chunk.metadata.setdefault("parent_id", str(doc_id))
                chunk.metadata.setdefault("parent_id", str(doc_id))
            chunks.extend(doc_chunks)
        return chunks

    def stats(self, chunks: list[Chunk]) -> dict[str, Any]:
        if not chunks:
            return {"count": 0, "avg_len": 0, "max_len": 0}
        lengths = [len(c.text) for c in chunks]
        return {
            "count": len(chunks),
            "avg_len": sum(lengths) / len(lengths),
            "max_len": max(lengths),
            "strategy": self.strategy_name,
        }


def chunk_fingerprint(chunks: list[Chunk]) -> str:
    """Content hash for cache-busting an index."""
    material = "\n".join(c.text for c in chunks)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


__all__ = ["Chunk", "ChunkManager", "ChunkSplitter", "chunk_fingerprint"]
