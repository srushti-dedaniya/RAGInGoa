"""Fixed-size (window + overlap) chunking.

The workhorse baseline. Splits text into windows of ``size`` characters with
``overlap`` characters of carry-over so boundary context is never torn.
"""

from __future__ import annotations

from rag.chunking.chunk_manager import Chunk, ChunkSplitter


class FixedSizeChunker(ChunkSplitter):
    """Window-based splitter with configurable overlap."""

    name = "fixed"

    def __init__(self, size: int = 500, overlap: int = 80, **_: object) -> None:
        super().__init__(size=size, overlap=overlap)
        if overlap >= size:
            raise ValueError("overlap must be smaller than size")

    def split_text(self, text: str, doc_id: str, metadata: dict) -> list[Chunk]:
        if not text.strip():
            return []
        chunks: list[Chunk] = []
        start = 0
        total = len(text)
        step = self.size - self.overlap
        n = 0
        while start < total:
            end = min(start + self.size, total)
            piece = text[start:end]
            chunks.append(
                Chunk(
                    text=piece,
                    chunk_id=f"{doc_id}-c{n}",
                    metadata=dict(metadata),
                    start_char=start,
                    end_char=end,
                    strategy=self.name,
                )
            )
            n += 1
            if end == total:
                break
            start += step
        return chunks


__all__ = ["FixedSizeChunker"]