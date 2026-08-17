# RAGInGoa Frontend

React + Vite + Tailwind single-page app. **Don't type. Just ask.**

## Run

```bash
npm install
npm run dev        # http://localhost:5173
```

## Modes

- `VITE_USE_DEMO=true` — fully offline, canned responses (no backend needed).
- default — talks to the FastAPI backend at `VITE_API_BASE_URL`; falls back to
  demo mode automatically when the backend is unreachable.

## Build

```bash
npm run build      # -> dist/
npm run preview
```

## Structure

- `src/components/` — Navbar, Hero, VoiceButton, Waveform, QueryWorkspace,
  Transcript, AnswerCard, SourceCard, Pipeline, Chunking, Benchmark, Guardrails,
  SystemStatus, Footer
- `src/hooks/` — `useVoiceRecorder`, `usePipeline`, `useScrollAnimation`
- `src/services/` — `api`, `voiceService`, `ragService`
- `src/context/RAGContext.jsx` — shared state for health + query turns
- `src/styles/` — global + design tokens + animations