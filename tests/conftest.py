"""Pytest bootstrap: ensure the repo root is importable (rag, backend, scripts)."""

from __future__ import annotations

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("STT_ROUTER", "dev")
os.environ.setdefault("LLM_ROUTER", "dev")
os.environ.setdefault("EMBEDDING_MODEL", "hashing")
os.environ.setdefault("REQUIRE_INDEX", "false")
os.environ.setdefault("SIMILARITY_THRESHOLD", "0")
for path in (ROOT, ROOT / "backend", ROOT / "scripts"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
