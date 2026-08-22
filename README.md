# RAGInGoa

> **A multilingual, voice-enabled Retrieval-Augmented Generation system for intelligent question answering.**

RAGInGoa is a voice-first RAG system built for **Hacker House Goa 2026 — Task 2**. It combines speech recognition, semantic retrieval, vector search, LLM-based generation, and guardrails into a single conversational pipeline.

Users can ask questions through **voice or text** in **English, Hindi, or Marathi** and receive context-aware responses through an intelligent routing pipeline.

---

## Overview

RAGInGoa is designed around a simple principle:

> **Retrieve when relevant context exists. Generate naturally when it doesn't.**

The system determines whether a query is relevant to the provided knowledge base.

- **RAG-relevant query** → semantic retrieval → grounded answer
- **General query** → LLM-based response
- **Unsafe / invalid query** → guardrail handling

This prevents the system from blindly answering every question through retrieval while maintaining grounded responses for knowledge-base queries.

---

## Architecture

```text
                    ┌─────────────────┐
                    │      User       │
                    │   Voice / Text  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Sarvam STT    │
                    │ Speech-to-Text  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Query Router   │
                    └────────┬────────┘
                             │
                   ┌──────────┴──────────┐
                   ▼                     ▼
            RAG Relevant            General Query
                   │                     │
                   ▼                     ▼
            Query Embedding             LLM
                   │                     │
                   ▼                     │
             FAISS Search                │
                   │                     │
                   ▼                     │
            Retrieved Context            │
                   │                     │
                   ▼                     │
           Grounded Generation           │
                   │                     │
                   └──────────┴──────────┘
                             ▼
                    ┌─────────────────┐
                    │    Guardrails   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Final Answer   │
                    │   + Listen      │
                    └─────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (for containerized deployment)

---

### Local Development (No Docker)

#### Backend
```bash
cd backend
cp .env.example .env
# Edit .env: set STT_ROUTER=dev, LLM_ROUTER=dev, REQUIRE_INDEX=false
pip install -r requirements.txt
pip install -r ../rag/requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Backend runs at `http://localhost:8000` | Docs at `http://localhost:8000/docs`

#### Frontend
```bash
cd frontend
cp .env.example .env
# Edit .env: set VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`

---

### Docker (Production-like)

#### Build & Run Both Services
```bash
# From repo root
docker compose up --build
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

#### Build Backend Only
```bash
docker build -f backend/Dockerfile -t ragingoa-backend .
docker run -d -p 8000:8000 \
  -e STT_ROUTER=dev \
  -e LLM_ROUTER=dev \
  -e REQUIRE_INDEX=false \
  -e CORS_ORIGINS="http://localhost:5173" \
  ragingoa-backend
```

#### Build Frontend Only
```bash
docker build -f frontend/Dockerfile -t ragingoa-frontend frontend
docker run -d -p 5173:80 \
  -e VITE_API_BASE_URL=http://localhost:8000 \
  ragingoa-frontend
```

---

### Production Deployment

#### Render (Backend)
1. Create Web Service → Runtime: **Docker**
2. Dockerfile: `backend/Dockerfile` | Context: `.` (repo root)
3. Environment variables:
   ```
   SARVAM_API_KEY=<your-key>
   OPENAI_API_KEY=<your-key>
   LLM_ROUTER=openai
   STT_ROUTER=sarvam
   REQUIRE_INDEX=true
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   ```
4. Plan: **Starter ($7/mo)** or higher (512MB Free tier insufficient)

#### Vercel (Frontend)
1. Import project → Root Directory: `frontend`
2. Environment variable:
   ```
   VITE_API_BASE_URL=https://your-render-backend.onrender.com
   ```

---

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# Text query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Best time to visit Palolem?", "language_code": "en-IN"}'

# Voice query (multipart)
curl -X POST http://localhost:8000/api/rag/voice \
  -F "file=@audio.webm" \
  -F "language_code=en-IN"

# TTS
curl -X POST http://localhost:8000/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "language_code": "en-IN"}' \
  --output output.wav
```

---

### Project Structure
```
RAGInGoa/
├── backend/           # FastAPI + Gunicorn
│   ├── app/           # Routes, services, models
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/          # Vite + React + Tailwind
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── rag/               # Core RAG package (Python)
│   ├── chunking/
│   ├── embeddings/
│   ├── retrieval/
│   ├── vector_db/
│   └── requirements.txt
├── scripts/           # build_index.py, download_dataset.py
├── docker-compose.yml
└── README.md
```

---

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STT_ROUTER` | `dev` \| `sarvam` | `dev` |
| `LLM_ROUTER` | `dev` \| `openai` | `dev` |
| `SARVAM_API_KEY` | Sarvam AI key (required for prod) | — |
| `OPENAI_API_KEY` | OpenAI key (required for prod) | — |
| `REQUIRE_INDEX` | Fail if FAISS index missing | `true` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `localhost:5173,localhost:3000` |
| `VITE_API_BASE_URL` | Frontend → Backend URL | `http://localhost:8000` |
