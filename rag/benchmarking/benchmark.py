"""End-to-end pipeline benchmarking.

Measures per-stage latency (embed, insert, retrieve, generate) across a set of
queries against the sample corpus and emits a JSON report.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rag.benchmarking.latency import LatencyStats
from rag.dataset.loader import read_data
from rag.chunking.chunk_manager import ChunkManager
from rag.embeddings.embedder import get_embedder
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig
from rag.vector_db.index import build_index

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "rag" / "data" / "samples" / "sample_goa_docs.jsonl"
INDEX_DIR = ROOT / "rag" / "vector_db" / "index"


class BenchmarkRunner:
    """Runs a latency micro-benchmark and stores a dict report."""

    def __init__(self, strategy: str = "sentence", top_k: int = 4) -> None:
        self.strategy = strategy
        self.top_k = top_k
        self.embedder = get_embedder()
        self._ensure_index(strategy)
        self.retriever = Retriever(
            self.embedder,
            self.index,
            RetrievalConfig(top_k=top_k),
        )

    def _ensure_index(self, strategy: str) -> None:
        docs = read_data(SAMPLES)
        chunks = ChunkManager(strategy).split(docs)
        self.index = build_index(self.embedder, chunks, INDEX_DIR)

    def _time(self, fn) -> tuple[float, object]:
        started = time.perf_counter()
        result = fn()
        return (time.perf_counter() - started) * 1000, result

    def run(self, queries: list[str], repetitions: int = 1) -> dict:
        stats = LatencyStats()
        hits_at_k: list[int] = []
        for _ in range(max(1, repetitions)):
            for query in queries:
                ms, _ = self._time(lambda: self.embedder.embed(query))
                stats.add("embed", ms)
                ms, results = self._time(
                    lambda q=query: self.retriever.retrieve(q, top_k=self.top_k)
                )
                stats.add("retrieve", ms)
                hits_at_k.append(len(results))
                ms, _ = self._time(lambda r=results: self._fake_generate(query, r))
                stats.add("generate", ms)
        return {
            "strategy": self.strategy,
            "top_k": self.top_k,
            "queries": len(queries),
            "repetitions": max(1, repetitions),
            "index_size": self.index.size(),
            "latency": stats.summary(),
            "total_avg_ms": stats.total_avg_ms,
            "avg_hits_per_query": round(sum(hits_at_k) / max(1, len(hits_at_k)), 2),
        }

    def _fake_generate(self, query: str, results: list[dict]) -> str:
        time.sleep(0.001)
        return f"Based on {len(results)} sources, about '{query}'"


def run_benchmark(
    queries: list[str] | None = None,
    top_k: int = 4,
    repetitions: int = 1,
    out: str | None = None,
) -> dict:
    if not queries:
        queries = [
            "When is the best time to visit Palolem?",
            "What should I eat in Goa?",
            "How do I reach Dudhsagar Falls?",
            "Where is the Latin Quarter of Panaji?",
            "Which churches are must-sees in Old Goa?",
        ]
    report = BenchmarkRunner(top_k=top_k).run(queries, repetitions=repetitions)
    if out:
        target = Path(out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RAGInGoa latency benchmark.")
    parser.add_argument("--queries", type=int, default=5, help="Number of sample queries")
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--out", default=str(ROOT / "rag" / "benchmarking" / "results" / "last_run.json"))
    args = parser.parse_args(argv)
    report = run_benchmark(
        top_k=args.top_k,
        repetitions=args.repetitions,
        out=args.out,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())