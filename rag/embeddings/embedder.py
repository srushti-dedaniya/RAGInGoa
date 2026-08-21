"""Embedding providers.

``get_embedder`` returns the best available provider: sentence-transformers when
installed, otherwise a deterministic hashing embedder so the pipeline runs
offline without breaking imports.
"""

from __future__ import annotations

import hashlib
import logging
import math
from functools import lru_cache

logger = logging.getLogger(__name__)


class Embedder:
    """Common interface for embedding providers."""

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]

    def model_name(self) -> str:
        raise NotImplementedError


class HashingEmbedder(Embedder):
    """Deterministic, dependency-free embedder for dev mode.

    Each token contributes to several neighbouring buckets via a seeded hash in
    a sliding window (a poor-man's local hashing). The vector is L2-normalised,
    so cosine search behaves sensibly even with this weak signal.
    """

    def __init__(self, dim: int = 384, window: int = 3) -> None:
        super().__init__(dim=dim)
        self.window = max(1, int(window))

    def _tokens(self, text: str) -> list[str]:
        norm = text.lower()
        return [tok for tok in norm.split() if tok]

    def _window_hashes(self, text: str) -> list[int]:
        toks = self._tokens(text)
        if not toks:
            return []
        hashes: list[int] = []
        for i in range(len(toks)):
            for w in range(1, self.window + 1):
                if i + w > len(toks):
                    break
                grams = " ".join(toks[i : i + w])
                hashes.append(int(hashlib.sha256(grams.encode("utf-8")).hexdigest()[:8], 16))
        return hashes

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        hashes = self._window_hashes(text)
        if not hashes:
            return vec
        for h in hashes:
            base = h % self.dim
            for j in range(3):
                bucket = (base + j) % self.dim
                sign = 1.0 if ((h >> j) & 1) else -1.0
                vec[bucket] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1e-9
        return [v / norm for v in vec]

    def model_name(self) -> str:
        return f"hashing-{self.dim}"


class SentenceTransformerEmbedder(Embedder):
    """Wrapper around sentence-transformers, imported lazily."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dim: int = 384) -> None:
        super().__init__(dim=dim)
        from sentence_transformers import SentenceTransformer  # optional dep

        # The index build/setup step downloads the model. Runtime must use that
        # cached copy instead of issuing slow Hugging Face metadata requests.
        self._model = SentenceTransformer(model_name, local_files_only=True)
        self._name = model_name

    @lru_cache(maxsize=512)
    def embed(self, text: str) -> list[float]:
        return self._model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=False).tolist()

    def model_name(self) -> str:
        return self._name


@lru_cache(maxsize=4)
def get_embedder(model_name: str = "all-MiniLM-L6-v2", dim: int = 384, allow_fallback: bool = True) -> Embedder:
    """Return SentenceTransformerEmbedder when available, else HashingEmbedder."""
    if model_name.lower() in {"dev", "hashing", "test"}:
        return HashingEmbedder(dim=dim)
    try:
        return SentenceTransformerEmbedder(model_name=model_name, dim=dim)
    except ImportError:  # pragma: no cover - runs only when lib missing
        if not allow_fallback:
            raise RuntimeError("sentence-transformers is required for production indexing")
        logger.warning(
            "sentence-transformers not installed; using dev HashingEmbedder(dim=%d)", dim
        )
        return HashingEmbedder(dim=dim)


__all__ = ["Embedder", "HashingEmbedder", "SentenceTransformerEmbedder", "get_embedder"]
