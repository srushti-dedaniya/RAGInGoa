"""RAGInGoa RAG package.

Speak a question. We retrieve the signal. You get a grounded answer.

## Layout

- `dataset/`    — load / clean / download source documents
- `chunking/`   — fixed-size, sentence, semantic and metadata-aware splitters
- `embeddings/` — dev (hashing) and sentence-transformers embedders
- `vector_db/`  — in-memory numpy index with cosine search, persisting to disk
- `retrieval/`  — retriever + reranker with a shared config
- `evaluation/` — hit@k / recall@k metrics on tagged test queries
- `benchmarking/` — end-to-end latency micro-benchmarks (p50/p95/p99)
- `experiments/` — comparisons of chunking strategies and top_k
- `data/samples/` — small curated Goa document set for the demo

## Dev-first philosophy

No API keys needed. `get_embedder()` falls back to a deterministic hashing
embedder; the vector index is pure numpy; sample docs ship in the repo. Swap in
`SentenceTransformerEmbedder`, point config at a chromadb/milvus router and the
same `Retriever` interface keeps working.

## Quickstart

```bash
pip install -r rag/requirements.txt
python -c "
import sys; sys.path.insert(0, '.')
from rag.dataset.loader import read_data
from rag.chunking.chunk_manager import ChunkManager
from rag.embeddings.embedder import get_embedder
from rag.vector_db.index import build_index, load_index
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig

docs = read_data('rag/data/samples/sample_goa_docs.jsonl')
chunks = ChunkManager('sentence').split(docs)
emb = get_embedder()
idx = build_index(emb, chunks, 'rag/vector_db/index')
retriever = Retriever(emb, idx, RetrievalConfig(top_k=3))
for hit in retriever.retrieve('best time to visit Palolem'):
    print(hit['score'], '-', hit['text'][:70])
"
```

## Benchmark

```bash
python rag/benchmarking/benchmark.py --queries 10 --stages
python rag/evaluation/retrieval_eval.py
python rag/experiments/chunking_comparison.py
```