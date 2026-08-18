"""Hierarchical document/child chunking with parent summaries in metadata."""
from __future__ import annotations

from rag.chunking.chunk_manager import Chunk, ChunkSplitter
from rag.chunking.sentence_based import SentenceChunker


class HierarchicalChunker(ChunkSplitter):
    name = "hierarchical"

    def __init__(self, size: int = 500, overlap: int = 80, parent_size: int = 1800, **kwargs: object) -> None:
        super().__init__(size=size, overlap=overlap)
        self.parent_size = max(size, int(parent_size))
        self.child = SentenceChunker(size=size, overlap=overlap, **kwargs)

    def split_text(self, text: str, doc_id: str, metadata: dict) -> list[Chunk]:
        chunks: list[Chunk] = []
        for parent_pos, start in enumerate(range(0, len(text), self.parent_size)):
            parent_text = text[start:start + self.parent_size]
            parent_id = f"{doc_id}-p{parent_pos}"
            for child in self.child.split_text(parent_text, parent_id, metadata):
                child.strategy = self.name
                child.start_char += start
                child.end_char += start
                child.metadata = {**child.metadata, "parent_id": parent_id, "parent_position": parent_pos}
                chunks.append(child)
        return chunks


__all__ = ["HierarchicalChunker"]
