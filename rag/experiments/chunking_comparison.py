"""Compare chunking strategies on split quality + retrieval hit@k."""

from __future__ import annotations

from rag.dataset.loader import read_data
from rag.chunking.chunk_manager import ChunkManager
from rag.embeddings.embedder import get_embedder
from rag.vector_db.index import build_index
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "rag" / "data" / "samples" / "sample_goa_docs.jsonl"
INDEX_DIR = ROOT / "rag" / "vector_db" / "index"

QUERIES = [
    ("When is the best time to visit Palolem?", "beaches"),
    ("What should I eat in Goa?", "food"),
    ("How do I reach Dudhsagar Falls?", "travel"),
]


def run_chunking_comparison() -> dict:
    docs = read_data(SAMPLES)
    embedder = get_embedder()
    results: dict[str, dict] = {}
    for strategy in ("fixed", "sentence", "semantic"):
        chunks = ChunkManager(strategy).split(docs)
        index = build_index(embedder, chunks, INDEX_DIR)
        retriever = Retriever(embedder, index, RetrievalConfig(top_k=2))
        topics_hit = 0
        for query, topic in QUERIES:
            hits = retriever.retrieve(query, top_k=2)
            if any(h.get("metadata", {}).get("topic") == topic for h in hits):
                topics_hit += 1
        results[strategy] = {
            "chunk_count": len(chunks),
            "avg_len": round(sum(len(c.text) for c in chunks) / max(1, len(chunks)), 1),
            "query_hit_rate": topics_hit / len(QUERIES),
        }
    return results


def main() -> int:
    import json

    print(json.dumps(run_chunking_comparison(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())