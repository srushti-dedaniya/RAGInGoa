# RAGInGoa Backend

FastAPI service powering the **Voice → RAG → Answer** pipeline.

```
POST /api/query        { "query": "When is the best time to visit Palolem?" }
POST /api/transcribe   multipart audio file -> { transcript, confidence, latency_ms }
GET  /api/health       system status + active routers
GET  /api/benchmark    last benchmark run
POST /api/benchmark    run a fresh latency benchmark
```

## Quick start

```bash
pip install -r backend/requirements.txt
cp .env.example .env            # dev defaults work with no keys
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

The **dev router** mode needs no API keys — STT, LLM and the vector DB all fall
back to deterministic offline implementations, so the whole API works on a cold
clone. Set `STT_ROUTER=whisper`, `LLM_ROUTER=openai`,
`VECTOR_DB_ROUTER=chromadb` and fill `OPENAI_API_KEY` to unlock real engines.

## Routers

| Setting | Values | Notes |
| --- | --- | --- |
| `STT_ROUTER` | `dev` \| `whisper` | whisper requires OpenAI key |
| `LLM_ROUTER` | `dev` \| `openai` | openai uses gpt-4o-mini |
| `VECTOR_DB_ROUTER` | `dev` \| `chromadb` \| `milvus` \| `qdrant` | dev = numpy index |

## Pipeline stages

`transcribe → retrieve → rerank → generate → guardrails` — every stage reports
its own latency in the response (`latency_breakdown`), and failures degrade to
graceful partial results instead of 500s (see `app/harness/error_handler.py`).