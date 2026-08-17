# Demo Script

~5 minute live demo. **Less noise. More signal.**

## Setup (before the demo)

```bash
python scripts/setup.py
python scripts/build_index.py
uvicorn app.main:app --reload --port 8000 --app-dir backend
cd frontend && npm run dev
```

Open http://localhost:5173 in a fresh incognito window.

## Script

### 1. Landing (0:00–0:45)
- **How it works:** hero, "Don't type. Just ask.", SYSTEM ONLINE badge (live from
  `/api/health`), animated pipeline with orbiting STT / VECTOR SEARCH / RAG tags.
- Call out the three badges: HH GOA 2026 · TASK #02, VOICE → RAG → ANSWER.

### 2. Voice query (0:45–1:45)
- Click **TRY VOICE** (navbar) or the central mic blob.
- Ask: *"When is the best time to visit Palolem?"*
- Watch the pipeline light up: STT → VECTOR SEARCH → RERANK → GENERATION →
  GUARDRAILS.
- Show the **grounded answer** with `[Source: …]` citations and the confidence.

### 3. Sources & guardrails (1:45–2:45)
- Scroll to **Sources** — each card shows title, topic tag, score, and a copyable
  chunk id (cite button).
- Open the **Guardrails** section — four checks light up green with reasons.
- Emphasise: anything ungrounded would be flagged, not hallucinated.

### 4. Performance (2:45–3:45)
- Scroll to **Performance**, hit **Run benchmark**.
- Walk the latency table (p50/p95/p99 per stage) — dev mode is sub-10ms end-to-end.
- Note: real LLM stage is the dominant cost; we isolate it so numbers stay honest.

### 5. Failure resilience (3:45–4:30) — optional flex
- Stop the backend, watch the UI flip to **demo mode** (canned responses + banner).
- Restart it: SYSTEM ONLINE returns automatically (health poll every 30s).

### 6. Close (4:30–5:00)
- "Speak a question. We retrieve the signal. You get a grounded answer."
- Point judges to `docs/` for the engineering story (chunking experiments,
  retrieval eval, guardrail design).

## Fallbacks

- No mic → type in the query workspace and hit **Ask**.
- Backend down → `VITE_USE_DEMO=true` runs the whole UI offline.
- No audio file → `/api/transcribe` accepts any supported audio file.