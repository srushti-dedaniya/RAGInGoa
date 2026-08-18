"""One-shot project setup: create dirs, install deps, bootstrap .env files."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: list[str], cwd: Path) -> None:
    print(f"\n$ {' '.join(cmd)}  (in {cwd.name})")
    subprocess.check_call(cmd, cwd=cwd)


def ensure_dirs() -> None:
    dirs = [
        ROOT / "rag" / "data" / "raw",
        ROOT / "rag" / "data" / "processed",
        ROOT / "rag" / "vector_db" / "index",
        ROOT / "rag" / "benchmarking" / "results",
        ROOT / "backend" / "benchmark_results",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"ensure {d.relative_to(ROOT)}/")


def bootstrap_env() -> None:
    # Keep each runtime self-contained: repository commands read the root file,
    # FastAPI can be launched from ``backend/``, and Vite only exposes values
    # from its own project directory. Never replace an existing local config.
    targets = [
        ROOT / ".env",
        ROOT / "backend" / ".env",
        ROOT / "frontend" / ".env",
    ]
    for target in targets:
        example = target.parent / f"{target.name}.example"
        if not target.exists() and example.exists():
            shutil.copy(example, target)
            print(f"created {target.relative_to(ROOT)} from {example.relative_to(ROOT)}")


def install(scope: str) -> None:
    if scope in ("rag", "all"):
        _run([sys.executable, "-m", "pip", "install", "-r", "rag/requirements.txt"], ROOT)
    if scope in ("backend", "all"):
        _run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], ROOT)
    if scope in ("frontend", "all"):
        if shutil.which("npm"):
            _run(["npm", "install"], ROOT / "frontend")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bootstrap the RAGInGoa workspace.")
    parser.add_argument("--scope", choices=["rag", "backend", "frontend", "all"], default="all")
    parser.add_argument("--no-install", action="store_true", help="skip dependency install")
    args = parser.parse_args(argv)

    ensure_dirs()
    bootstrap_env()
    if not args.no_install:
        install(args.scope)
    print("\nDone. See README.md for the next steps (build_index, uvicorn, npm run dev).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
