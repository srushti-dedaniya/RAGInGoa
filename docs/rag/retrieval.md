# Retrieval

Retrieval is the "signal" stage: turn a query into the most relevant chunks.

## Flow

```
query → embed → cosine top-k → rerank → top N chunks
```

`rag/retrieval/retriever.py` provides the `Retriever`:

```python
from rag.retrieval.retriever import Retriever
from rag.retrieval.retrieval_config import RetrievalConfig
from rag.vector_db.index import load_index
from rag.embeddings.embedder import get_embedder

embedder = get_embedder()
index = load_index("rag/vector_db/index", model_name=embedder.model_name())
retriever = Retriever(embedder, index, RetrievalConfig(top_k=4, score_threshold=0.0, rerank=False))

for hit in retriever.retrieve("best time to visit Palolem"):
    print(hit["score"], hit["text"][:80])
```

## Index

The dev index (`rag/vector_db/index.py`) is a numpy matrix + JSON sidecar:

- `add(ids, vectors, metadata)` / `search(vector, top_k)` — cosine via `rag/vector_db/search.py`.
- Persisted as `<model>.npy` + `<model>_meta.json`; `build_index()` and
  `load_index()` are the public entry points.

Production routers (chromadb / milvus / qdrant) expose the same interface.

## Reranker

`rag/retrieval/reranker.py` re-orders hits. Dev mode blends the cosine score
(0.8) with query–chunk lexical overlap (0.2) — a cheap stand-in for a
cross-encoder. Enable with `RetrievalConfig(rerank=True)`.

## Config (`RetrievalConfig`)

| Field | Default | Purpose |
| --- | --- | --- |
| `top_k` | 4 | chunks returned to the generator |
| `score_threshold` | 0.0 | drop chunks below this cosine score |
| `rerank` | False | run the reranking pass |

## Evaluation

`rag/evaluation/retrieval_eval.py` measures **hit@k**, **recall@k** and **MRRT**
against `test_queries.json` (tagged with expected topics). On the sample corpus
with the dev embedder and `top_k=3`, hit@3 ≈ 0.80.

`rag/evaluation/answer_eval.py` adds answer-side metrics: token-recall
faithfulness and a grounding ratio (fraction of sources cited).

## Reproduce

```bash
python rag/evaluation/retrieval_eval.py        # full report
python rag/experiments/retrieval_comparison.py # top_k sweep
```