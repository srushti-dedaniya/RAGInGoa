"""Vector database configuration and router selection."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VectorConfig:
    """Settings for the deployed vector store."""

    router: str = "dev"  # dev | chromadb | milvus | qdrant
    path: str = "rag/vector_db/index"
    metric: str = "cosine"
    dimension: int = 384
    collection: str = "ragingoa"
    url: str = "http://localhost:19530"
    extra: dict = field(default_factory=dict)


__all__ = ["VectorConfig"]