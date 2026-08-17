"""In-memory vector index with disk persistence.

The dev index stores chunk vectors as a numpy matrix and the payload (ids,
texts, metadata) as sidecar JSON. Bucketed cosine search keeps demo queries
fast; swap ``VectorDBRouter`` for chromadb/milvus in production.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from rag.vector_db.search import search_index


def _slug(model_name: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", model_name.lower()).strip("-")


def _meta_file(path: Path, slug: str) -> Path:
    return path / f"{slug}_meta.json"


def _vec_file(path: Path, slug: str) -> Path:
    return path / f"{slug}.npy"


@dataclass
class SearchResult:
    """A single hit returned by the index."""

    chunk_id: str
    text: str
    metadata: dict
    score: float
    score_type: str


class VectorIndex:
    """Cosine index built on a numpy matrix."""

    def __init__(
        self,
        metric: str = "cosine",
        model_name: str = "unknown",
        vectors: np.ndarray | None = None,
        ids: list[str] | None = None,
        texts: list[str] | None = None,
        meta: list[dict] | None = None,
    ) -> None:
        self.metric = metric
        self.model_name = model_name
        self.vectors = vectors if vectors is not None else np.zeros((0, 0), dtype=np.float64)
        self.ids: list[str] = ids or []
        self.texts: list[str] = texts or []
        self.meta: list[dict] = meta or []

    def add(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict],
        texts: list[str] | None = None,
    ) -> None:
        mat = np.asarray(vectors, dtype=np.float64)
        if mat.ndim == 1:
            mat = mat.reshape(1, -1)
        if self.vectors.shape[1] == 0:
            self.vectors = mat
        else:
            self.vectors = np.vstack([self.vectors, mat])
        self.ids.extend(ids)
        self.meta.extend(metadata)
        self.texts.extend(texts or ["" for _ in ids])

    def search(self, vector: list[float], top_k: int = 4) -> list[SearchResult]:
        return search_index(self, vector, top_k)

    def size(self) -> int:
        return len(self.ids)

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        slug = _slug(self.model_name)
        np.save(_vec_file(p, slug), self.vectors)
        payload = {
            "model_name": self.model_name,
            "metric": self.metric,
            "ids": self.ids,
            "texts": self.texts,
            "meta": self.meta,
        }
        _meta_file(p, slug).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, path: str | Path, model_name: str = "unknown") -> "VectorIndex":
        p = Path(path)
        slug = _slug(model_name)
        vec_file = _vec_file(p, slug)
        meta_file = _meta_file(p, slug)
        if not vec_file.exists() or not meta_file.exists():
            raise FileNotFoundError(f"no index at {p} for model '{model_name}'")
        vectors = np.load(vec_file)
        payload = json.loads(meta_file.read_text(encoding="utf-8"))
        return cls(
            metric=payload.get("metric", "cosine"),
            model_name=payload.get("model_name", model_name),
            vectors=vectors,
            ids=payload.get("ids", []),
            texts=payload.get("texts", []),
            meta=payload.get("meta", []),
        )


class ChromaVectorIndex(VectorIndex):
    """Optional chromadb-backed wrapper. Kept separate so import never fails
    when chromadb is missing."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        raise RuntimeError("ChromaVectorIndex requires 'pip install chromadb' and configuration")


def build_index(
    embedder,
    chunks: list,
    path: str | Path = "rag/vector_db/index",
) -> VectorIndex:
    """Embed chunks and persist a fresh index to ``path``."""
    if not chunks:
        vectors = np.zeros((0, embedder.dim), dtype=np.float64)
        index = VectorIndex(model_name=embedder.model_name(), vectors=vectors)
        index.save(path)
        return index

    texts = [c.text for c in chunks]
    vectors = embedder.embed_batch(texts)
    ids = [c.chunk_id for c in chunks]
    meta = [dict(c.metadata) for c in chunks]
    index = VectorIndex(model_name=embedder.model_name())
    index.add(ids, vectors, meta, texts=texts)
    index.save(path)
    return index


def load_index(
    path: str | Path = "rag/vector_db/index",
    model_name: str = "unknown",
) -> VectorIndex | None:
    """Load an existing index, or None when there is nothing on disk."""
    if not Path(path).exists():
        return None
    try:
        return VectorIndex.load(path, model_name=model_name)
    except FileNotFoundError:
        return None


__all__ = ["SearchResult", "VectorIndex", "build_index", "load_index"]