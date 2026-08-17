# API Documentation

Base URL: `http://localhost:8000` — Swagger UI at `/docs`, OpenAPI at `/openapi.json`.

Interactive API reference: `VITE_API_BASE_URL` in the frontend `.env` points at
this service.

## Endpoints

### `GET /api/health`

System status, active routers, index size, uptime.

```json
{
  "service": "RAGInGoa",
  "status": "ONLINE",
  "version": "1.0.0",
  "uptime_seconds": 421.2,
  "routers": { "stt": "dev", "llm": "dev", "vector_db": "dev" },
  "index_size": 9,
  "ready": true
}
```

### `POST /api/query`

Run a full RAG turn over typed text.

**Request**
```json
{ "query": "When is the best time to visit Palolem?", "top_k": 4 }
```

**Response**

| Field | Type | Meaning |
| --- | --- | --- |
| `query` | string | normalized query |
| `answer` | string | grounded answer |
| `sources` | list | retrieved chunks: `text`, `chunk_id`, `metadata`, `score`, `score_type` |
| `confidence` | float 0–1 | mean guardrail score |
| `guardrails` | object | `{passed, checks:[{name,passed,reason,score}]}` |
| `latency_breakdown` | object | `{stt, retrieval, generation, guardrails, total}` ms |
| `engine` | object | `{stt, llm, vector_db, embedding}` |
| `intermediate` | object | transcript + retrieval counts |
| `warnings` | list | non-critical failures |

### `POST /api/transcribe`

Multipart upload (`file` field) → transcript.

```json
{ "transcript": "…", "confidence": 1.0, "engine": "whisper-1", "latency_ms": 823.0 }
```

Limits: 25 MB, audio content-types (`wav`, `webm`, `mp3`, `ogg`, `mpeg`).

### `GET /api/benchmark`

Returns the most recent benchmark report.

### `POST /api/benchmark`

Runs a fresh latency benchmark (optional `{queries, top_k}`) and returns the
report with `summary`.

## Errors

| Code | Meaning |
| --- | --- |
| 400 | invalid input / empty upload |
| 413 | audio too large |
| 415 | unsupported audio content-type |
| 500 | pipeline failure (always JSON: `{error, message, status_code, stage, detail}`) |

## CORS

Allowed origins come from `CORS_ORIGINS` (defaults:
`http://localhost:5173,http://localhost:3000`).