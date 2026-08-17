"""Embedding configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EmbeddingConfig:
    """Provider-agnostic embedding settings."""

    model_name: str = "all-MiniLM-L6-v2"
    dim: int = 384
    batch_size: int = 32
    provider: str = "auto"  # auto | hashing | sentence-transformers


DEFAULT_EMBEDDING_CONFIG = EmbeddingConfig()

__all__ = ["EmbeddingConfig", "DEFAULT_EMBEDDING_CONFIG"]