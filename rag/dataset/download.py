"""Fetch raw datasets into ``rag/data/raw``.

Designed to fail gracefully offline. With no ``--url`` the script explains how a
real corpus would be fetched and exits 0, keeping the demo usable on a cold
clone.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path


KNOWN_DATASETS = {
    "goa-brochure": None,
    "goa-heritage": None,
    "wikipedia-goa": None,
}


def _download(url: str, out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {url} -> {out_file}")
    try:
        urllib.request.urlretrieve(url, out_file)  # noqa: S310
    except urllib.error.URLError as exc:
        print(f"download failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"saved {out_file.stat().st_size} bytes")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download a raw dataset for RAGInGoa.")
    parser.add_argument(
        "--dataset",
        choices=sorted(KNOWN_DATASETS),
        default="wikipedia-goa",
        help="Named dataset slot for the file",
    )
    parser.add_argument("--url", default=None, help="Direct URL of a JSONL/JSON source")
    parser.add_argument(
        "--out",
        default="rag/data/raw",
        help="Destination directory (default: rag/data/raw)",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out)
    if not args.url:
        print(
            "No --url provided; nothing downloaded. A real corpus (e.g. an "
            "exported Wikipedia dump, a Goa tourism brochure corpus, or scraped "
            "heritage texts) would land here. The repo ships curated samples in "
            "rag/data/samples/ so the full pipeline works offline."
        )
        return 0

    name = args.dataset
    if not name.endswith(".jsonl"):
        name = f"{name}.jsonl"
    _download(args.url, out_dir / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())