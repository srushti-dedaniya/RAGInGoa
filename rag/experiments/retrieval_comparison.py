"""Compare retrieval quality across top_k values."""

from __future__ import annotations

from rag.dataset.loader import read_data
from rag.chunking.chunk_manager import ChunkManager
from rag.embeddings.embedder import get_embedder
from rag.vector_db.index import build_index, load_index
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "rag" / "data" / "samples" / "sample_goa_docs.jsonl"
INDEX_DIR = ROOT / "rag" / "vector_db" / "index"

TOPICS = {
    "When is the best time to visit Palolem?": "beaches",
    "What should I eat in Goa?": "food",
    "How do I reach Dudhsagar Falls?": "travel",
    "Where is the Latin Quarter of Panaji?": "heritage",
    "Which churches are must-sees in Old Goa?": "heritage",
    "What is the cheapest way to get around Goa?": "transport",
}


def run_retrieval_comparison(top_ks: tuple[int, ...] = (2, 4, 8)) -> dict:
    docs = read_data(SAMPLES)
    embedder = get_embedder()
    chunks = ChunkManager("sentence").split(docs)
    index = load_index(INDEX_DIR, model_name=embedder.model_name()) or build_index(
        embedder, chunks, INDEX_DIR
    )
    report: dict[str, dict] = {}
    for k in top_ks:
        retriever = Retriever(embedder, index, RetrievalConfig(top_k=k))
        hits = 0
        for query, topic in TOPICS.items():
            results = retriever.retrieve(query, top_k=k)
            if any(r.get("metadata", {}).get("topic") == topic for r in results):
                hits += 1
        report[f"top-{k}"] = {
            "topic_hit_rate": hits / len(TOPICS),
            "avg_results": k,
        }
    return report


def main() -> int:
    import json

    print(json.dumps(run_retrieval_comparison(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())