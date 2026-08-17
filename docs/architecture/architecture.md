# Architecture

**RAGInGoa** is a voice-driven Retrieval-Augmented Generation system built for
HH Goa 2026 (Task #02): **Don't type. Just ask.**

![RAGInGoa pipeline](pipeline-diagram.png)

## High-level flow

```
VOICE IN → STT → QUERY WORKSPACE → RETRIEVAL → RERANK → GENERATION → GUARDRAILS → GROUNDED ANSWER
```

| Stage | Owner | Responsibility |
| --- | --- | --- |
| STT | `backend/app/services/stt_service.py` | Audio → text. `dev` router returns a canned transcript; `whisper` router calls OpenAI Whisper. |
| Query workspace | `backend/app/harness/pipeline.py` | Normalises the transcript, sanitises input, selects `top_k`. |
| Retrieval | `rag/retrieval/retriever.py` | Embeds the query and searches the vector index (cosine top-k). |
| Rerank | `rag/retrieval/reranker.py` | Second-pass re-ordering (lexical + score blend in dev). |
| Generation | `backend/app/services/generation_service.py` | Grounded answer citing the retrieved passages. |
| Guardrails | `backend/app/guardrails/*` | Safety, relevance, grounding and refusal checks. |
| Answer | `backend/app/models/response.py` | Structured response: answer + sources + confidence + latency. |

## Repositories

- **`rag/`** — retrieval core: dataset loading, chunking strategies, embeddings,
  vector index, retrieval, evaluation and benchmarking. Runs on stdlib + numpy.
- **`backend/`** — FastAPI service that composes the retrieval core into the
  voice pipeline and exposes the HTTP API.
- **`frontend/`** — React + Vite + Tailwind single-page app (Voice UI, transcripts,
  grounded answers, source cards, benchmark and guardrail dashboards).

## Router philosophy

Every provider dependency is abstracted behind a *router* so the system runs
fully offline with deterministic, dependency-free implementations:

| Router | dev mode | Production |
| --- | --- | --- |
| `STT_ROUTER` | canned transcript | `whisper` (OpenAI API) |
| `LLM_ROUTER` | extractive, source-citing generator | `openai` (gpt-4o-mini grounding prompt) |
| `VECTOR_DB_ROUTER` | in-memory numpy index, persisted to disk | `chromadb` / `milvus` / `qdrant` |

Swapping a router never changes the calling code — the same interfaces are used
by the pipeline regardless of backend.

## Failure semantics

- Every stage is wrapped (`app/harness/error_handler.py`) and a failure degrades
  to a *graceful partial result*, never a bare 500.
- Non-critical stages that fail are recorded in `warnings` so the UI can surface
  them without destroying the answer.
- Retries use exponential backoff + jitter (`app/harness/retry.py`).

## Data flow (dev)

1. `scripts/setup.py` creates the workspace and installs dependencies.
2. `scripts/build_index.py` reads `rag/data/samples/*.jsonl` (or processed docs),
   chunks with the configured strategy, embeds, and writes a numpy index +
   JSON sidecar to `rag/vector_db/index/`.
3. The backend lazy-builds the same index on first request when the index file
   is missing, so a cold clone just works.
4. The frontend calls `/api/query`; every response includes per-stage latency so
   the UI can animate the pipeline.

## Reproducing numbers

- Retrieval quality: `python rag/evaluation/retrieval_eval.py`
- Latency: `python scripts/run_benchmark.py`
- Experiments: `python rag/experiments/chunking_comparison.py`, `python rag/experiments/retrieval_comparison.py`

See `docs/performance/benchmarking.md` and `docs/performance/latency-results.md`.