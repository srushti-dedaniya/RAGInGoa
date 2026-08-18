# RAGInGoa

HH Goa 2026 Task 2 — Voice-Enabled RAG. The existing React/Vite interface is backed by a FastAPI orchestration harness, Sarvam speech recognition, MSMARCO-XI retrieval, grounded generation, and deterministic guardrails.

## Architecture

```text
Voice / text → validation → Sarvam STT (voice) → normalization → safety check
→ query embedding → persistent FAISS search → threshold/context selection
→ grounded generation → grounding validation → structured API response → React UI
```

The index and embedding model load once per backend process. Document embeddings are produced only by the indexing command; requests embed only the normalized query. `/api/rag/voice` executes voice-to-answer in one backend request, so the Sarvam key never reaches the browser.

## Dataset and indexing

The production corpus is [ai4bharat/MSMARCO-XI](https://huggingface.co/datasets/ai4bharat/MSMARCO-XI). The loader uses its real `query`, `Answer`, `query_id`, `query_type`, `passages.is_selected`, `English_passages`, `Translated_passages`, `Eng_Query`, and `Eng_Answer` schema. It removes blank/very short and duplicate passages and preserves language, split, query, answer, selection, passage position, and source metadata.

```powershell
python scripts/download_dataset.py --language hi --split validation --limit 5000
python scripts/build_index.py --strategy sentence
```

`--limit 0` processes the complete split. A bounded default keeps a laptop/demo build practical and reproducible. The index command fails if the semantic embedding dependency is unavailable; it never silently creates a hashing index. Artifacts are persisted under `rag/vector_db/index/` as FAISS, NumPy portability, and JSON metadata files. Runtime fails clearly when the configured index is absent and `REQUIRE_INDEX=true`; it does not rebuild on a request.

## Chunking

`CHUNKING_STRATEGY=sentence` is the default because MSMARCO passages are prose and sentence boundaries preserve meaning at low indexing cost.

- `fixed`: character windows with configurable overlap.
- `sentence`: sentence-boundary packing up to a target size, with overlap.
- `semantic`: topic breaks from lexical coherence changes between adjacent sentences.
- `metadata`: wraps another strategy and prefixes selected document metadata so retrieved slices remain self-describing.
- `hierarchical`: creates parent windows and sentence-aware child chunks, retaining parent IDs and offsets.

Every chunk contains `document_id`, `chunk_id`, `parent_id`, `source`, `position`, `chunking_strategy`, `text_length`, offsets, and dataset metadata.

## Retrieval, harness, and guardrails

`all-MiniLM-L6-v2` (384 dimensions, normalized vectors) is the configurable low-latency default. FAISS `IndexFlatIP` performs cosine-equivalent search over normalized embeddings. `TOP_K` and `SIMILARITY_THRESHOLD` bound the context. The harness records stage latency, retries bounded external failures, and formats one response contract.

Safety and prompt-injection patterns exit before retrieval/generation. Results below the threshold exit without an LLM call. Retrieved documents are delimited as untrusted data and cannot override the system prompt. Generation requires JSON output and source citations. A deterministic post-check requires a retrieved source identifier; an unverified answer is replaced with an honest fallback. These controls reduce risk; they do not claim hallucinations are impossible.

## Setup

Python 3.10+ and Node 18+ are required.

```powershell
python -m pip install -r rag/requirements.txt -r backend/requirements.txt -r requirements-dev.txt
Copy-Item .env.example .env
python scripts/download_dataset.py --language hi --split validation --limit 5000
python scripts/build_index.py
python -m uvicorn app.main:app --app-dir backend --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Docker deployment remains available with `docker compose up --build`; production notes are in `deployment/README.md`.

## Environment

Copy `.env.example` and set:

- `SARVAM_API_KEY` (required for real voice), `SARVAM_STT_MODEL`, `SARVAM_LANGUAGE_CODE`
- `LLM_API_KEY` and `LLM_MODEL` (required for real generation)
- `EMBEDDING_MODEL`, `EMBEDDING_DIM`, `VECTOR_DB_PATH`
- `DATASET_PATH`, `DATASET_LANGUAGE`, `DATASET_SPLIT`, `DATASET_MAX_RECORDS`
- `CHUNKING_STRATEGY`, `CHUNK_SIZE`, `CHUNK_OVERLAP`
- `TOP_K`, `SIMILARITY_THRESHOLD`, `REQUIRE_INDEX`, `CORS_ORIGINS`

No credential is committed or returned to the frontend. `STT_ROUTER=dev`, `LLM_ROUTER=dev`, and `REQUIRE_INDEX=false` exist only for deterministic automated tests/local diagnostics and are not the production defaults.

## API

- `GET /health` and `GET /api/health`
- `POST /api/rag/query` (preferred) and `POST /api/query` (frontend compatibility): `{"query":"...","top_k":4}`
- `POST /api/rag/voice`: multipart field `file`, optional query parameter `top_k`
- `POST /api/transcribe`: Sarvam transcript only (compatibility/diagnostics)
- `POST /api/benchmark`: benchmark service

Query responses contain `success`, `query`, `answer`, `sources`, `grounded`, `latency_ms`, stage timings, engine details, and guardrail results. Errors use HTTP status codes and do not expose secrets or tracebacks.

## Testing and latency

```powershell
python -m pytest
cd frontend
npm test
npm run build
cd ..
python scripts/run_benchmark.py --queries 100 --repetitions 1
```

The benchmark measures warm query preprocessing, embedding, persistent-index retrieval, context selection, generation, grounding, and total RAG latency. It records hardware/model/index size and P50, P70, P100, mean, min, max, and sample count in `rag/benchmarking/results/last_run.json`. Voice latency is deliberately separate because Sarvam and network latency are external. A local result is added only after an actual run; the project never claims full voice-to-answer is under 200 ms.

For an end-to-end voice check, start both services, permit microphone access, record a clip under 30 seconds, and submit it. Browser → `/api/rag/voice` → Sarvam → retrieval → generation → grounded response is the tested contract. A live Sarvam/LLM call requires valid credentials and available provider credits.
