import math

from rag.embeddings.embedder import HashingEmbedder


def test_hashing_embedder_deterministic():
    embedder = HashingEmbedder(dim=384)
    first = embedder.embed("When is the best time to visit Palolem?")
    second = embedder.embed("When is the best time to visit Palolem?")
    assert first == second


def test_hashing_embedder_normalized():
    embedder = HashingEmbedder(dim=384)
    vec = embedder.embed("beaches are nice in November")
    norm = math.sqrt(sum(v * v for v in vec))
    assert abs(norm - 1.0) < 1e-6


def test_hashing_embedder_dim():
    embedder = HashingEmbedder(dim=128)
    assert len(embedder.embed("anything")) == 128
    assert embedder.dim == 128


def test_batch_matches_single():
    embedder = HashingEmbedder(dim=96, window=2)
    batch = embedder.embed_batch(["one two", "three four"])
    assert batch[0] == embedder.embed("one two")
    assert len(batch) == 2