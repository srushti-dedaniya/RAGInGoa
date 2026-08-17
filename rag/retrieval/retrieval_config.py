"""Retrieval configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RetrievalConfig:
    top_k: int = 4
    score_threshold: float = 0.0
    rerank: bool = False
    rerank_top_k: int = 8
    extra: dict = field(default_factory=dict)


__all__ = ["RetrievalConfig"]