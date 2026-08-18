"""Measured warm RAG benchmark; never rebuilds the index or fabricates timings."""
from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

from backend.app.config.settings import get_settings
from backend.app.services.generation_service import GenerationService
from rag.embeddings.embedder import get_embedder
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig
from rag.vector_db.index import load_index

ROOT = Path(__file__).resolve().parents[2]

def _stats(values: list[float]) -> dict:
    arr = np.asarray(values, dtype=float)
    return {"p50_ms": round(float(np.percentile(arr, 50)), 3),
            "p70_ms": round(float(np.percentile(arr, 70)), 3),
            "p100_ms": round(float(np.max(arr)), 3), "mean_ms": round(float(np.mean(arr)), 3),
            "min_ms": round(float(np.min(arr)), 3), "max_ms": round(float(np.max(arr)), 3),
            "count": len(values)}

def run_benchmark(queries: list[str] | None = None, top_k: int = 4, repetitions: int = 1,
                  out: str | None = None, query_count: int = 100,
                  include_generation: bool = False) -> dict:
    settings = get_settings()
    embedder = get_embedder(settings.EMBEDDING_MODEL, settings.EMBEDDING_DIM,
                            allow_fallback=False)
    index = load_index(settings.index_path, embedder.model_name())
    if not index or not index.size():
        raise RuntimeError("persistent index missing; build it before benchmarking")
    retriever = Retriever(embedder, index, RetrievalConfig(top_k=top_k))
    generator = GenerationService(settings) if include_generation else None
    queries = queries or [m.get("query") or m.get("english_query") or " ".join(t.split()[:12])
                          for m, t in zip(index.meta, index.texts)]
    queries = list(dict.fromkeys(q for q in queries if q))[:max(1, query_count)]
    retriever.retrieve(queries[0], top_k)  # warm models and index
    totals: list[float] = []
    stages = {name: [] for name in ("preprocess", "embedding", "retrieval", "context", "generation", "grounding")}
    for _ in range(max(1, repetitions)):
        for raw in queries:
            total_start = time.perf_counter()
            start = time.perf_counter(); query = " ".join(raw.split()); stages["preprocess"].append((time.perf_counter()-start)*1000)
            start = time.perf_counter(); vector = embedder.embed(query); stages["embedding"].append((time.perf_counter()-start)*1000)
            start = time.perf_counter(); hits = index.search(vector, top_k); stages["retrieval"].append((time.perf_counter()-start)*1000)
            start = time.perf_counter(); context = [{"chunk_id": h.chunk_id, "text": h.text, "metadata": h.metadata, "score": h.score} for h in hits if h.score >= settings.SIMILARITY_THRESHOLD]; stages["context"].append((time.perf_counter()-start)*1000)
            start = time.perf_counter(); answer = generator.generate(query, context)["answer"] if include_generation and context else ""; stages["generation"].append((time.perf_counter()-start)*1000)
            start = time.perf_counter(); _ = bool(answer and "[Source:" in answer); stages["grounding"].append((time.perf_counter()-start)*1000)
            totals.append((time.perf_counter()-total_start)*1000)
    report = {"run_at": datetime.now(timezone.utc).isoformat(), "queries": len(totals),
              "warm": True, "hardware": platform.platform(), "embedding_model": embedder.model_name(),
              "generation_model": settings.LLM_MODEL if settings.LLM_ROUTER != "dev" else "test-extractive",
              "scope": "end-to-end" if include_generation else "local semantic RAG (external LLM excluded)",
              "index_size": index.size(), "top_k": top_k, "rag_latency": _stats(totals),
              "stages": {k: _stats(v) for k, v in stages.items()}}
    report["latency"] = {"retrieve": report["stages"]["retrieval"]}
    if out:
        target = Path(out); target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=int, default=100)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--include-generation", action="store_true")
    parser.add_argument("--out", default=str(ROOT / "rag/benchmarking/results/last_run.json"))
    args = parser.parse_args(argv)
    report = run_benchmark(top_k=args.top_k, repetitions=args.repetitions,
                           out=args.out, query_count=args.queries,
                           include_generation=args.include_generation)
    print(json.dumps(report, indent=2, ensure_ascii=False)); return 0

if __name__ == "__main__": raise SystemExit(main())
