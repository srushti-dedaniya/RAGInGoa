# Backend. Build context must be the REPO ROOT (so ../rag is available):
#   docker build -f backend/Dockerfile -t ragingoa-backend .
# docker-compose handles this automatically.

FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/workspace:/rag \
    PORT=8000 \
    REQUIRE_INDEX=true

WORKDIR /workspace

# System dependencies for faiss-cpu
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Core RAG package (sibling of backend/)
COPY rag/ ./rag/
COPY rag/requirements.txt ./rag-requirements.txt

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./rag-requirements.txt -r ./requirements.txt

COPY backend/app ./backend/app
COPY scripts/ ./scripts/

# Download dataset and build index for all supported languages at build time
ARG MSMARCO_LIMIT=5000
RUN python scripts/download_dataset.py --language en --split validation --limit ${MSMARCO_LIMIT} && \
    python scripts/download_dataset.py --language hi --split validation --limit ${MSMARCO_LIMIT} && \
    python scripts/download_dataset.py --language mr --split validation --limit ${MSMARCO_LIMIT} && \
    python scripts/build_index.py --language en --strategy sentence && \
    python scripts/build_index.py --language hi --strategy sentence && \
    python scripts/build_index.py --language mr --strategy sentence && \
    test -s rag/data/processed/msmarco_xi_en.jsonl && \
    test -s rag/data/processed/msmarco_xi_hi.jsonl && \
    test -s rag/data/processed/msmarco_xi_mr.jsonl && \
    test -s rag/vector_db/index/en/all-minilm-l6-v2.faiss && \
    test -s rag/vector_db/index/hi/all-minilm-l6-v2.faiss && \
    test -s rag/vector_db/index/mr/all-minilm-l6-v2.faiss && \
    test -s rag/vector_db/index/en/all-minilm-l6-v2_meta.json && \
    test -s rag/vector_db/index/hi/all-minilm-l6-v2_meta.json && \
    test -s rag/vector_db/index/mr/all-minilm-l6-v2_meta.json

# Gunicorn config for production
COPY deployment/backend/gunicorn.conf.py /workspace/gunicorn.conf.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["gunicorn", "-c", "/workspace/gunicorn.conf.py", "backend.app.main:app"]