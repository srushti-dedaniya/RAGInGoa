"""Load document corpora from disk.

Supported formats: ``.jsonl`` (one JSON object per line) and ``.json`` (a list
of documents or a dict keyed by ``documents``). Every document is normalised to
``{"content": str, "metadata": dict}``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _normalise(item: dict[str, Any], index: int) -> dict[str, Any]:
    content = item.get("content") or item.get("text") or ""
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)
    metadata = dict(item.get("metadata") or {})
    metadata.setdefault("id", metadata.get("id") or f"doc-{index:04d}")
    metadata.setdefault("source", metadata.get("source") or "unknown")
    return {"content": content.strip(), "metadata": metadata}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if isinstance(item, dict) and ("content" in item or "text" in item):
            docs.append(_normalise(item, len(docs)))
    return docs


def read_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("documents") or payload.get("items") or []
    if not isinstance(payload, list):
        raise ValueError(f"unexpected JSON structure in {path}")
    docs: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict) and ("content" in item or "text" in item):
            docs.append(_normalise(item, len(docs)))
    return docs


def read_data(path: str | Path) -> list[dict[str, Any]]:
    """Read a corpus file and return ``[{content, metadata}]``."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"corpus file not found: {p}")
    if p.suffix == ".jsonl":
        return read_jsonl(p)
    return read_json(p)


__all__ = ["read_data"]