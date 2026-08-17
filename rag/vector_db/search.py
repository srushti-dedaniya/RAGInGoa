"""Fuzzy / ANN search over an in-memory index.

``search_index`` is the generic cosine top-k entry used by ``Retriever``. With
the dev numpy index this is an exhaustive scan, which is fine at demo scale.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from rag.vector_db.index import SearchResult, VectorIndex


def search_index(
    index: "VectorIndex",
    query_vector: list[float],
    top_k: int = 4,
) -> list["SearchResult"]:
    """Return ``top_k`` SearchResult ordered by descending cosine similarity."""
    from rag.vector_db.index import SearchResult  # deferred: avoids circular import

    if index.size() == 0:
        return []
    q = np.asarray(query_vector, dtype=np.float64)
    if q.ndim == 2:
        q = q[0]
    q_norm = np.linalg.norm(q)
    if q_norm == 0:
        q = q
    scores = index.vectors @ q
    order = np.argsort(-scores)[: min(top_k, index.size())]
    results: list[SearchResult] = []
    for pos in order:
        i = int(pos)
        results.append(
            SearchResult(
                chunk_id=index.ids[i],
                text=index.texts[i],
                metadata=index.meta[i],
                score=float(scores[i]),
                score_type=index.metric,
            )
        )
    return results


__all__ = ["search_index"]