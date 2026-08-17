"""Sentence-based chunking.

Splits on sentence boundaries and packs sentences until a target size, keeping
each chunk linguistically whole. Best default for retrieval + grounding.
"""

from __future__ import annotations

import re
from rag.chunking.chunk_manager import Chunk, ChunkSplitter

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")


class SentenceChunker(ChunkSplitter):
    """Packs whole sentences into chunks up to ``size`` characters."""

    name = "sentence"

    def __init__(
        self,
        size: int = 500,
        overlap: int = 0,
        min_sentence_len: int = 12,
        **_: object,
    ) -> None:
        super().__init__(size=size, overlap=overlap)
        self.min_sentence_len = int(min_sentence_len)

    def _sentences(self, text: str) -> list[str]:
        parts = _SENTENCE_SPLIT.split(text)
        out: list[str] = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if len(part) > self.size * 2:
                out.extend(p.strip() for p in self._hard_split(part))
            else:
                out.append(part)
        return out

    def _hard_split(self, part: str) -> list[str]:
        pieces: list[str] = []
        cursor = 0
        while cursor < len(part):
            end = cursor + self.size
            if end < len(part):
                cut = part.rfind(" ", cursor, end)
                if cut - cursor < self.min_sentence_len:
                    cut = end
            else:
                cut = len(part)
            pieces.append(part[cursor:cut])
            cursor = cut
        return pieces

    def _locate(self, text: str, sentences: list[str]) -> list[tuple[str, int]]:
        located: list[tuple[str, int]] = []
        cursor = 0
        for sentence in sentences:
            idx = text.find(sentence, cursor)
            if idx == -1:
                idx = cursor
            located.append((sentence, idx))
            cursor = idx + len(sentence)
        return located

    def split_text(self, text: str, doc_id: str, metadata: dict) -> list[Chunk]:
        located = self._locate(text, self._sentences(text))
        chunks: list[Chunk] = []
        buf: list[str] = []
        buf_len = 0
        buf_start = located[0][1] if located else 0
        n = 0
        for sentence, start in located:
            if buf and buf_len + len(sentence) > self.size:
                joined = " ".join(buf)
                chunks.append(
                    Chunk(
                        text=joined,
                        chunk_id=f"{doc_id}-c{n}",
                        metadata=dict(metadata),
                        start_char=buf_start,
                        end_char=buf_start + len(joined),
                        strategy=self.name,
                    )
                )
                n += 1
                buf = []
                buf_len = 0
            if not buf:
                buf_start = start
            buf.append(sentence)
            buf_len += len(sentence) + 1
        if buf:
            joined = " ".join(buf)
            chunks.append(
                Chunk(
                    text=joined,
                    chunk_id=f"{doc_id}-c{n}",
                    metadata=dict(metadata),
                    start_char=buf_start,
                    end_char=buf_start + len(joined),
                    strategy=self.name,
                )
            )
        return chunks


__all__ = ["SentenceChunker"]