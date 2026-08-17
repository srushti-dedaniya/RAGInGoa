# Team Video Script

~90 second submission video. Tone: energetic, demo-forward, "we built this so
it works offline".

## Script

### Hook (0:00–0:08)
> **Nobody should have to type a question to a machine.**

On-screen: hero, blurred, mic blob pulsing.

### The problem (0:08–0:20)
> "Hackathons ask you to *talk* to your data. Most RAG demos die the second the
> Wi-Fi drops. Ours doesn't."

Cut to: `SYSTEM ONLINE`, dev routers, no API keys.

### The build (0:20–0:40)
- STT router (dev/whisper), vector index, retriever + reranker.
- Four guardrails: safety, relevance, grounding, refusal.
- Every stage reports its own latency.

### The demo (0:40–1:15)
> "What's the best time to visit Palolem?"

Show: waveform → transcript → animated pipeline → grounded answer with sources
and green guardrails → benchmark table.

### Close (1:15–1:30)
> "Voice in. Context out. Grounded answers. **Less noise. More signal.**"

Logos: HH Goa 2026 · RAGInGoa v1.0.

## Production notes

- 1080p, 30fps, system fonts (Anton / Be Vietnam Pro / Space Mono).
- Capture from a real browser (not a screen-saver mock).
- Keep the benchmark visible: numbers are the flex.
- Mention the repo: `rag/`, `backend/`, `frontend/`, tests, docs, CI.