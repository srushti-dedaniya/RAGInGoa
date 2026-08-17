"""Pytest bootstrap: ensure the repo root is importable (rag, backend, scripts)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for path in (ROOT, ROOT / "backend", ROOT / "scripts"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))