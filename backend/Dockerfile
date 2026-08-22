# Backend. Build context must be the REPO ROOT (so ../rag is available):
#   docker build -f backend/Dockerfile -t ragingoa-backend .
# docker-compose handles this automatically.

FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/rag \
    PORT=8000 \
    REQUIRE_INDEX=true

WORKDIR /app

# System dependencies for faiss-cpu
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Core RAG package (sibling of backend/)
COPY rag/ /rag/
COPY rag/requirements.txt /app/rag-requirements.txt

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/rag-requirements.txt -r /app/requirements.txt

# Pre-download sentence-transformers model to avoid runtime download
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Download dataset and build index at build time
COPY scripts/ /app/scripts/
RUN python scripts/download_dataset.py --language hi --split validation --limit 5000 --out rag/data/processed/msmarco_xi.jsonl \
    && python scripts/build_index.py --strategy sentence --out rag/vector_db/index

# Gunicorn config for production
COPY deployment/backend/gunicorn.conf.py /app/gunicorn.conf.py

COPY backend/app /app/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["gunicorn", "-c", "/app/gunicorn.conf.py", "app.main:app"]
