"""Semantic-aware chunking (lightweight, model-free).

Real semantic segmenters use embeddings to detect topic breaks. This "dev
semantic" chunker approximates that signal with lexical similarity between
consecutive sentences and merges runs that stay above a coherence floor. It is a
deterministic stand-in so the full pipeline runs offline; swap the similarity
function for an embedding-based one when a model is available.
"""

from __future__ import annotations

import re
from rag.chunking.chunk_manager import Chunk, ChunkSplitter
from rag.chunking.sentence_based import SentenceChunker

_PUNCT = re.compile(r"[.,;:!?()\"']")
_STOP = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "at", "for", "with",
    "is", "are", "was", "were", "be", "it", "its", "this", "that", "as", "by",
}


def lexical_similarity(a: str, b: str) -> float:
    """Jaccard similarity on token sets (the dev coherence signal)."""
    ta = {w for w in _PUNCT.sub(" ", a.lower()).split() if w not in _STOP}
    tb = {w for w in _PUNCT.sub(" ", b.lower()).split() if w not in _STOP}
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


class SemanticChunker(SentenceChunker):
    """Sentence-level chunker that breaks on coherence drops."""

    name = "semantic"

    def __init__(
        self,
        size: int = 500,
        overlap: int = 0,
        min_sentence_len: int = 12,
        merge_threshold: float = 0.05,
        **_: object,
    ) -> None:
        super().__init__(
            size=size,
            overlap=overlap,
            min_sentence_len=min_sentence_len,
        )
        self.merge_threshold = float(merge_threshold)

    def split_text(self, text: str, doc_id: str, metadata: dict) -> list[Chunk]:
        located = self._locate(text, self._sentences(text))
        if not located:
            return []

        chunks: list[Chunk] = []
        buf: list[str] = []
        buf_start = located[0][1]
        n = 0
        prev = located[0][0]
        for sentence, start in located[1:]:
            coherence = lexical_similarity(prev, sentence)
            too_large = buf and sum(len(s) for s in buf) + len(sentence) > self.size
            if buf and (coherence < self.merge_threshold or too_large):
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
            if not buf:
                buf_start = start
            buf.append(sentence)
            prev = sentence

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


__all__ = ["SemanticChunker", "lexical_similarity"]