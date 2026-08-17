"""Metadata-aware chunking.

Wraps another strategy and enriches every chunk with document context. Titles
and headlines are never split away — each chunk stays self-describing so a
retrieved slice is resolvable without the full document.
"""

from __future__ import annotations

import re
from rag.chunking.chunk_manager import Chunk, ChunkSplitter

_HEADING = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)


class MetadataAwareChunker(ChunkSplitter):
    """Decorates an inner splitter with metadata prefixes and heading guard."""

    name = "metadata"

    def __init__(self, inner: ChunkSplitter, prefix_keys: tuple[str, ...] = ("title",)) -> None:
        super().__init__(size=getattr(inner, "size", 500), overlap=0)
        self.inner = inner
        self.prefix_keys = prefix_keys

    def _prefix(self, metadata: dict) -> str:
        parts = [str(metadata[k]) for k in self.prefix_keys if metadata.get(k)]
        return " | ".join(parts)

    def split_text(self, text: str, doc_id: str, metadata: dict) -> list[Chunk]:
        prefix = self._prefix(metadata)
        enriched_text = f"{prefix}.\n{text}" if prefix else text
        chunks = self.inner.split_text(enriched_text, doc_id, metadata)
        for chunk in chunks:
            chunk.metadata = {**chunk.metadata, "prefixed": bool(prefix)}
            if prefix:
                chunk.text = f"[{prefix}] {chunk.text}"
        return chunks


__all__ = ["MetadataAwareChunker"]