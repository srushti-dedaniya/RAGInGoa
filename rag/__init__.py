"""RAGInGoa — RAG core package.

Voice → RAG → Answer. This package implements the retrieval side of the
pipeline: data loading, chunking, embeddings, vector search, retrieval,
evaluation and benchmarking.

The entire package runs on stdlib + numpy in "dev mode" so a cold clone works
without GPU or API keys. Optional providers (sentence-transformers, chromadb,
openai) are wired in lazily and never break imports if missing.
"""

from rag.chunking.chunk_manager import Chunk, ChunkManager
from rag.embeddings.embedder import Embedder, get_embedder
from rag.vector_db.index import SearchResult, VectorIndex, build_index, load_index
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig

__all__ = [
    "Chunk",
    "ChunkManager",
    "Embedder",
    "get_embedder",
    "SearchResult",
    "VectorIndex",
    "build_index",
    "load_index",
    "Retriever",
    "RetrievalConfig",
]

__version__ = "1.0.0"