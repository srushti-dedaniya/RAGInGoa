# Backend. Build context must be the REPO ROOT (so ../rag is available):
#   docker build -f backend/Dockerfile -t ragingoa-backend .
# docker-compose handles this automatically.

FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/rag \
    PORT=8000

WORKDIR /app

# Core RAG package (sibling of backend/)
COPY rag/ /rag/

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/app /app/app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]