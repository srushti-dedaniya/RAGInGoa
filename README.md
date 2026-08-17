# RAGInGoa

**HH Goa 2026 · Task #02 — Voice → RAG → Answer**

> Don't type. Just ask. — *Speak a question. We retrieve the signal. You get a grounded answer.*

RAGInGoa is a voice-driven **Retrieval-Augmented Generation** (RAG) system. You speak a
question, it is transcribed, embedded, searched against a vector index of Goa context,
reranked, and grounded before an answer is generated. Four guardrails (safety, relevance,
grounding, refusal) verify every answer.

```
VOICE IN → STT → QUERY WORKSPACE → RETRIEVAL → RERANK → GENERATION → GUARDRAILS → GROUNDED ANSWER
```

![RAGInGoa pipeline](docs/architecture/pipeline-diagram.png)

**No API keys required.** Every provider has a *dev router* (offline, deterministic) so the
whole system runs on a clean clone. Swap in real providers (Whisper, OpenAI, chromadb) when
you're ready.

---

## 1. Prerequisites

| Tool | Version | Check |
| --- | --- | --- |
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Docker (optional) | 24+ | `docker --version` |

---

## 2. Quick Start (recommended path)

From the project root, in **three terminals**:

```bash
# Terminal 1 — build the vector index + run the backend
pip install -r rag/requirements.txt -r backend/requirements.txt -r requirements-dev.txt
python scripts/setup.py --no-install        # creates dirs + backend/.env
python scripts/build_index.py               # writes index (sample Goa corpus)
uvicorn app.main:app --reload --port 8000 --app-dir backend   # see note below
```

```bash
# Terminal 2 — frontend dev server
cd frontend
npm install
npm run dev
```

```bash
# Terminal 3 (optional) — verify with the live API
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"When is the best time to visit Palolem?"}'
```

> Windows (PowerShell): use `Copy-Item backend/.env.example backend/.env`, and the
> correct server command is `uvicorn app.main:app --reload --port 8000 --app-dir backend`.

Open **http://localhost:5173** → click **TRY VOICE** or the central mic blob → ask
*"When is the best time to visit Palolem?"*.

---

## 3. Step-by-Step (what each command does)

### 3.1 Bootstrap the workspace

```bash
python scripts/setup.py
```

- Creates empty data / index / benchmark directories.
- Copies `backend/.env.example` → `backend/.env` if missing.
- Optionally installs dependencies (`--scope rag|backend|frontend|all`).

### 3.2 Build the vector index

```bash
python scripts/build_index.py
```

- Reads the sample corpus (`rag/data/samples/sample_goa_docs.jsonl`).
- Chunks with the default `sentence` strategy, embeds with the dev hashing embedder.
- Writes `rag/vector_db/index/hashing-384.npy` + `hashing-384_meta.json`.

The backend also auto-builds this index on first request if it's missing, so this step is
optional but recommended (it makes startup instant).

### 3.3 Run the backend

```bash
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

From the project root. Interactive docs: **http://localhost:8000/docs**.

| Endpoint | Result |
| --- | --- |
| `GET /api/health` | system status, routers, index size |
| `POST /api/query` | `{query, top_k}` → grounded answer + sources + guardrails |
| `POST /api/transcribe` | multipart audio → transcript |
| `POST /api/benchmark` | run a latency benchmark |

### 3.4 Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**.

- The UI polls `/api/health` every 30 s; the badge flips between **SYSTEM ONLINE** and
  **SYSTEM DEGRADED**.
- Without a backend it **auto-falls back to demo mode** (canned responses + banner).
- For a fully offline demo: create `frontend/.env` with `VITE_USE_DEMO=true`.

### 3.5 Try it

- **Voice:** the central blob or navbar **TRY VOICE** → record → "Ask it". The pipeline
  animates STT → RETRIEVAL → RERANK → GENERATION → GUARDRAILS as it runs.
- **Text:** type in the query workspace and press **Ask**.
- **Guardrails:** scroll to the Guardrails section — the four checks light up with reasons.
- **Performance:** hit **Run benchmark** in the Performance section.

---

## 4. Docker (optional)

```bash
docker compose up --build
```

- Backend: http://localhost:8000/docs
- Frontend: http://localhost:5173

Nothing to install locally. Dev routers are the default. Production flavor:
`docker compose -f deployment/docker/docker-compose.prod.yml up` (see
`deployment/README.md`).

---

## 5. Tests & checks

```bash
# Python: full suite (rag + backend + integration)
pip install -r requirements-dev.txt
python -m pytest

# Frontend
cd frontend
npm run lint
npm test
npm run build
```

Currently **38 Python + 14 frontend** tests pass. CI replicates all of this in
`.github/workflows/`.

---

## 6. Benchmarks & evaluation

```bash
python scripts/run_benchmark.py --queries 10 --repetitions 3   # latency p50/p95/p99
python rag/evaluation/retrieval_eval.py                        # hit@k / recall@k / MRRT
python rag/experiments/chunking_comparison.py                  # strategy comparison
python rag/experiments/retrieval_comparison.py                 # top_k sweep
```

Baseline numbers live in `docs/performance/latency-results.md`.

---

## 7. Production routers (opt-in)

Set values in `backend/.env`, then restart the backend:

| Variable | Value | Effect |
| --- | --- | --- |
| `STT_ROUTER=whisper` | + `OPENAI_API_KEY` | real speech-to-text (Whisper API) |
| `LLM_ROUTER=openai` | + `OPENAI_API_KEY` | gpt-4o-mini grounded generation |
| `VECTOR_DB_ROUTER=chromadb` | + add container | real ANN vector store |
| `EMBEDDING_MODEL=all-MiniLM-L6-v2` | `pip install sentence-transformers` | real embeddings |

The `dev` routers are always a valid fallback and need zero configuration.

---

## 8. Environment variables

Every component ships a `.env.example`. Key ones:

| Env | Default | Meaning |
| --- | --- | --- |
| `STT_ROUTER` | `dev` | `dev` \| `whisper` |
| `LLM_ROUTER` | `dev` | `dev` \| `openai` |
| `VECTOR_DB_ROUTER` | `dev` | `dev` \| `chromadb` \| `milvus` \| `qdrant` |
| `OPENAI_API_KEY` | *(empty)* | Whisper / OpenAI routers |
| `CHUNK_STRATEGY` | `sentence` | `fixed` \| `sentence` \| `semantic` \| `metadata` |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `500` / `80` | chunk budget |
| `TOP_K` | `4` | chunks passed to the generator |
| `CORS_ORIGINS` | localhost:5173,3000 | allowed browser origins |
| `VITE_API_BASE_URL` | `http://localhost:8000` | frontend → backend URL |
| `VITE_USE_DEMO` | `false` | force offline demo responses |

---

## 9. Troubleshooting

| Problem | Fix |
| --- | --- |
| Port 8000 in use | `uvicorn ... --port 8001`, then set `VITE_API_BASE_URL=http://localhost:8001` |
| Frontend shows "System Degraded" | start the backend, or set `VITE_USE_DEMO=true` for offline mode |
| No microphone / mic blocked | allow the browser permission, refresh, or fall back to typed queries |
| `sentence-transformers not installed` | expected in dev mode — the hashing embedder is the fallback |
| `cp` not found (Windows) | `Copy-Item backend/.env.example backend/.env` (or run `scripts/setup.py`) |
| Slow first startup | it's the one-time index build; subsequent starts are instant |
| Tests failing on Windows paths | run from the repo root; `pytest.ini` sets `testpaths` for you |

---

## 10. Repository layout

```
RAGInGoa/
├── frontend/      React + Vite + Tailwind SPA (voice UI, answers, benchmarks)
├── backend/       FastAPI service (transcribe, query, benchmark, health) + guardrails
├── rag/           Python RAG core: dataset, chunking, embeddings, retrieval, eval, bench
├── tests/         backend / rag / integration pytest suites + frontend vitest
├── docs/          architecture, RAG strategy, performance, guardrails, API, demo
├── scripts/       setup, download_dataset, build_index, run_benchmark, make_diagram
├── deployment/    docker / nginx / gunicorn production configs
└── .github/       frontend + backend + tests CI workflows
```

## 11. Docs

- `docs/architecture/architecture.md` — system design & failure semantics
- `docs/rag/chunking-strategies.md` · `embeddings.md` · `retrieval.md`
- `docs/guardrails/guardrails.md`
- `docs/api/api-documentation.md` — full API reference
- `docs/demo/demo-script.md` — 5-minute live demo script

## 12. Team

**Less noise. More signal.** — System v1.0 · HH Goa 2026

## License

MIT — see `LICENSE`.