import numpy as np

from rag.embeddings.embedder import HashingEmbedder
from rag.vector_db.index import VectorIndex, build_index, load_index


def test_build_and_search(tmp_path):
    from rag.chunking.chunk_manager import ChunkManager

    embedder = HashingEmbedder(dim=64)
    chunks = []
    for i in range(6):
        chunks.extend(
            ChunkManager("sentence").split(
                [{"content": f"topic {i} content rocks", "metadata": {"id": f"d{i}"}}]
            )
        )
    index_dir = str(tmp_path / "idx")
    index = build_index(embedder, chunks, index_dir)
    assert index.size() == len(chunks)

    hits = index.search(embedder.embed("topic 3 content rocks"), top_k=2)
    assert len(hits) == 2
    assert hits[0].score >= hits[1].score
    assert hits[0].score_type == "cosine"


def test_save_load_roundtrip(tmp_path):
    from rag.chunking.chunk_manager import ChunkManager

    embedder = HashingEmbedder(dim=32)
    chunks = ChunkManager("sentence").split(
        [{"content": "persist me please and thank you", "metadata": {"id": "d1"}}]
    )
    index_dir = str(tmp_path / "idx")
    original = build_index(embedder, chunks, index_dir)

    loaded = load_index(index_dir, model_name=embedder.model_name())
    assert loaded is not None
    assert loaded.size() == original.size()
    assert loaded.ids[0] == original.ids[0]
    np.testing.assert_allclose(loaded.vectors, original.vectors)


def test_load_missing_returns_none(tmp_path):
    assert load_index(str(tmp_path / "nope"), model_name="x") is None


def test_empty_index_search(tmp_path):
    index = VectorIndex(model_name="e")
    assert index.search([0.1] * 8, top_k=3) == []