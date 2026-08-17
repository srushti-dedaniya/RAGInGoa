from pathlib import Path

from rag.chunking.chunk_manager import ChunkManager
from rag.embeddings.embedder import HashingEmbedder
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig
from rag.vector_db.index import build_index

SAMPLE = Path(__file__).resolve().parents[2] / "rag" / "data" / "samples" / "sample_goa_docs.jsonl"


def _retriever(strategy="sentence", top_k=4):
    from rag.dataset.loader import read_data

    docs = read_data(SAMPLE)
    chunks = ChunkManager(strategy).split(docs)
    embedder = HashingEmbedder(dim=96, window=3)
    index = build_index(embedder, chunks, "rag/vector_db/test-retrieval")
    return Retriever(embedder, index, RetrievalConfig(top_k=top_k))


def test_palolem_query_returns_beach_topic():
    retriever = _retriever(top_k=4)
    hits = retriever.retrieve("When is the best time to visit Palolem?", top_k=4)
    topics = [h["metadata"].get("topic") for h in hits]
    assert "beaches" in topics
    assert hits[0]["score"] > hits[-1]["score"]


def test_retrieve_with_details_shape():
    retriever = _retriever(top_k=3)
    details = retriever.retrieve_with_details("What should I eat in Goa?", top_k=3)
    assert details["top_k"] == 3
    assert details["index_size"] > 0
    assert "latency_ms" in details
    assert all({"text", "metadata", "score", "chunk_id"} <= set(r) for r in details["results"])


def test_rerank_keeps_top_results():
    retriever = _retriever(top_k=8)
    hits = retriever.retrieve("How do I reach Dudhsagar Falls?", top_k=4)
    assert len(hits) <= 4