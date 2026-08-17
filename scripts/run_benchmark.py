"""Run the RAGInGoa latency benchmark and print the JSON report."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.benchmarking.benchmark import main as benchmark_main

if __name__ == "__main__":
    raise SystemExit(benchmark_main(sys.argv[1:]))
