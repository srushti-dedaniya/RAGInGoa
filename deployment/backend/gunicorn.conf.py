# Gunicorn config for the RAGInGoa backend (production).
#
#   gunicorn -c deployment/backend/gunicorn.conf.py app.main:app
#
# Run from the repo root so `backend/` is importable, or set PYTHONPATH=/app.

import os

bind = "0.0.0.0:8000"
workers = int(os.environ.get("GUNICORN_WORKERS", "2"))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 60
graceful_timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"