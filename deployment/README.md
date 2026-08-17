# Deployment

RAGInGoa ships with two compose flavors:

- **`docker-compose.yml`** (repo root) — dev: builds both services, mounts the
  `rag/` package and the backend source, defaults to dev routers. Nothing to
  install locally.

  ```bash
  docker compose up --build
  # frontend  http://localhost:5173
  # backend   http://localhost:8000/docs
  ```

- **`deployment/docker/docker-compose.prod.yml`** — immutable images, env-driven
  routers. Consumes `deployment/backend/gunicorn.conf.py` and
  `deployment/frontend/nginx.conf` which are baked in by the respective images.

## Image build

Backend requires the **repo root** as Docker build context (it copies the
sibling `rag/` package):

```bash
docker build -f backend/Dockerfile -t ragingoa-backend .
docker build -f frontend/Dockerfile -t ragingoa-frontend frontend
```

## Routing config

| Env | Value | Meaning |
| --- | --- | --- |
| `STT_ROUTER` | `dev` | canned transcript (offline) |
| `STT_ROUTER` | `whisper` | OpenAI Whisper (needs `OPENAI_API_KEY`) |
| `LLM_ROUTER` | `dev` | extractive grounded generator |
| `LLM_ROUTER` | `openai` | gpt-4o-mini chat completion |
| `VECTOR_DB_ROUTER` | `dev` | in-memory numpy index (offline) |
| `VECTOR_DB_ROUTER` | `chromadb`/`milvus`/`qdrant` | ANN backend (add service to compose) |

## Static frontend

Nginx serves `/` as an SPA (`try_files … /index.html`) and reverse-proxies
`/api/*` to the backend container — so the browser never needs CORS in
deployment.