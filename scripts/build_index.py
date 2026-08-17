"""Build (or refresh) the dev vector index from processed/sample docs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.dataset.loader import read_data
from rag.chunking.chunk_manager import ChunkManager, chunk_fingerprint
from rag.embeddings.embedder import get_embedder
from rag.vector_db.index import build_index

from backend.app.config.settings import get_settings  # reuse backend settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the RAGInGoa vector index.")
    parser.add_argument("--data", default=None, help="corpus path (default: sample corpus)")
    parser.add_argument("--strategy", default=None, help="chunking strategy")
    parser.add_argument("--out", default=None, help="index output dir")
    args = parser.parse_args(argv)

    settings = get_settings()
    data_path = args.data or str(settings.sample_data_path)
    strategy = args.strategy or settings.CHUNK_STRATEGY
    out_dir = args.out or str(settings.index_path)

    docs = read_data(data_path)
    print(f"documents: {len(docs)}")

    chunk_config = {"size": settings.CHUNK_SIZE, "overlap": settings.CHUNK_OVERLAP}
    manager = ChunkManager(strategy, chunk_config)
    chunks = manager.split(docs)
    print(f"chunks ({strategy}): {len(chunks)}  stats={manager.stats(chunks)}")
    print(f"fingerprint: {chunk_fingerprint(chunks)}")

    embedder = get_embedder(model_name=settings.EMBEDDING_MODEL, dim=settings.EMBEDDING_DIM)
    index = build_index(embedder, chunks, out_dir)
    print(f"index written: {out_dir}  ({index.size()} vectors, model={embedder.model_name()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
