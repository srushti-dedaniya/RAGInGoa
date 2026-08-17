# Benchmarking

Latency is a feature. RAGInGoa measures every stage end-to-end and reports the
numbers inline in every API response.

## What is measured

`rag/benchmarking/benchmark.py` runs a configurable set of queries through the
full offline pipeline and records per-stage latencies:

| Stage | What it times |
| --- | --- |
| `embed` | embedding the query |
| `retrieve` | index search + (optional) rerank |
| `generate` | grounded answer generation |
| (pipeline) | STT, retrieval, generation, guardrails — reported by the API |

Aggregation lives in `rag/benchmarking/latency.py`: **avg, p50, p95, p99** via a
single pass over the numpy array.

## Run

```bash
python scripts/run_benchmark.py --queries 5 --top-k 4 --repetitions 3
```

Output is written to `rag/benchmarking/results/last_run.json` and printed.

The API exposes the same job:

```
GET  /api/benchmark   → last run (crafted from results file / in-memory)
POST /api/benchmark   → run now
```

## Methodology notes

- Dev-mode numbers exclude network LLM calls by design (generator is offline).
- Real OpenAI/Whisper paths are measured end-to-end in the API's
  `latency_breakdown`; `/api/benchmark` reports the dev micro-benchmark.
- p95/p99 matter more than avg for a demo: users notice tail latency.

## Interpreting results

See `docs/performance/latency-results.md` for the recorded baseline and how to
reproduce it on stage vs. laptop.