"""Download a raw dataset into rag/data/raw.

Thin wrapper around rag.dataset.download. Pass a direct --url for a real corpus;
with no url the script explains how the demo works offline.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.dataset.download import main as dataset_main

if __name__ == "__main__":
    raise SystemExit(dataset_main(sys.argv[1:]))
