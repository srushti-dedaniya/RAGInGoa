# Latency Results

Baseline recorded with the **dev routers** (offline, no API keys) on a typical
laptop and stage machine. Hardware variance is expected; the p50/p95 distribution
is what matters.

## Dev micro-benchmark

Command: `python scripts/run_benchmark.py --queries 5 --top-k 4`

Sample corpus: 9 documents → 9 sentence chunks → dev hashing embedder
(384-d). Index in memory: 9 vectors.

| Stage | avg | p50 | p95 | p99 |
| --- | ---: | ---: | ---: | ---: |
| embed | ~0.4 ms | ~0.3 ms | ~0.8 ms | ~1.0 ms |
| retrieve | ~1.1 ms | ~1.0 ms | ~1.8 ms | ~2.1 ms |
| generate | ~0.6 ms | ~0.6 ms | ~0.9 ms | ~1.0 ms |
| **total (approx)** | **~2.1 ms** | — | — | — |

## End-to-end query (API `latency_breakdown`)

One turn of `POST /api/query` in dev mode:

| Stage | Typical |
| --- | ---: |
| stt | 0 ms (already transcribed) |
| retrieval | ~1 ms |
| generation | ~0.1 ms |
| guardrails | ~1.6 ms |
| **total** | **~2.7 ms** |

## Scaling expectations

- **Index size:** exhaustive cosine is O(N) per query. At demo scale (<1k chunks)
  it is effectively instant. For 100k+ chunks, move `VECTOR_DB_ROUTER` to
  chromadb/milvus/qdrant — ANN keeps p95 flat instead of linear.
- **Embedder:** hashing embedder ≈ sub-ms. `all-MiniLM-L6-v2` adds 1–5 ms/query
  on CPU. On GPU it is negligible.
- **LLM:** the dominant cost in production (100–1000 ms). The UI shows the LLM
  stage independently so the latency story stays honest.

## Reproduce

```bash
python scripts/setup.py --scope rag --no-install
python scripts/build_index.py
python scripts/run_benchmark.py --queries 10 --repetitions 3
python -m pytest tests/rag -q      # asserts the benchmark harness works
```