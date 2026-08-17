"""Retrieval evaluation.

Builds a real index from the sample corpus, then reports hit@k / recall@k /
MRRT against the tagged ``test_queries.json``.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from rag.dataset.loader import read_data
from rag.chunking.chunk_manager import ChunkManager
from rag.embeddings.embedder import get_embedder
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig
from rag.vector_db.index import build_index, load_index
from rag.evaluation.metrics import hit_at_k, recall_at_k, mrrt

ROOT = Path(__file__).resolve().parents[2]
EVAL_DATA = Path(__file__).resolve().parent / "test_queries.json"
SAMPLES = ROOT / "rag" / "data" / "samples" / "sample_goa_docs.jsonl"
INDEX_DIR = ROOT / "rag" / "vector_db" / "index"


def build_retriever(strategy: str = "sentence", top_k: int = 4) -> Retriever:
    docs = read_data(SAMPLES)
    chunks = ChunkManager(strategy).split(docs)
    embedder = get_embedder()
    index = build_index(embedder, chunks, INDEX_DIR)
    return Retriever(
        embedder,
        index,
        RetrievalConfig(top_k=top_k, rerank=False),
    )


def _relevant(result: dict, topic: str, hint: list[str]) -> bool:
    meta = result.get("metadata", {})
    text = (result.get("text", "") or "").lower()
    if meta.get("topic") == topic:
        return True
    return any(h.lower() in text for h in hint)


def eval_retrieval(retriever: Retriever, queries: list[dict], k: int = 4) -> dict:
    rows = []
    for item in queries:
        results = retriever.retrieve(item["query"], top_k=k)
        relevant = [_relevant(r, item["expected_topic"], item.get("expected_sources_hint", []))
                    for r in results]
        total = len([h for h in results if relevant_for(h, item)])
        rows.append(
            {
                "query": item["query"],
                "hit@k": hit_at_k(relevant, k),
                "recall@k": recall_at_k(relevant, k, total),
                "mrrt": mrrt(relevant),
                "top_1": relevant[0] if relevant else False,
            }
        )
    total_queries = len(rows) or 1
    return {
        "k": k,
        "queries": len(rows),
        "hit_at_k": sum(r["hit@k"] for r in rows) / total_queries,
        "recall_at_k": sum(r["recall@k"] for r in rows) / total_queries,
        "mrrt": sum(r["mrrt"] for r in rows) / total_queries,
        "rows": rows,
    }


def relevant_for(result: dict, item: dict) -> bool:
    return _relevant(result, item["expected_topic"], item.get("expected_sources_hint", []))


def run_retrieval_eval(top_k: int = 4, strategy: str = "sentence") -> dict:
    retriever = build_retriever(strategy, top_k)
    queries = json.loads(EVAL_DATA.read_text(encoding="utf-8"))
    started = time.perf_counter()
    report = eval_retrieval(retriever, queries, k=top_k)
    report["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return report


def main(argv: list[str] | None = None) -> int:
    top_k = int(sys.argv[1]) if len(sys.argv or []) > 1 else 4
    report = run_retrieval_eval(top_k=top_k)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())