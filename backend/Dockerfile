# Backend. Build context must be the REPO ROOT (so ../rag is available):
#   docker build -f backend/Dockerfile -t ragingoa-backend .
# docker-compose handles this automatically.

FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/workspace \
    PORT=8000

WORKDIR /workspace

# Core RAG package (sibling of backend/)
COPY rag/ ./rag/
COPY rag/requirements.txt ./rag-requirements.txt

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./rag-requirements.txt -r ./requirements.txt

COPY backend/app ./backend/app
COPY scripts/ ./scripts/

# Dataset and vector artifacts are Git-ignored. Materialize all supported
# language corpora and indexes into the immutable deployment image.
ARG MSMARCO_LIMIT=1000
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

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"]
