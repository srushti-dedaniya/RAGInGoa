"""RAGInGoa backend package.

Bootstrap: ensures the repo root is importable so the ``rag`` package resolves
regardless of how uvicorn is launched.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))