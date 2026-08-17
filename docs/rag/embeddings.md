# Embeddings

Embeddings map text to vectors so cosine distance becomes a proxy for meaning.
RAGInGoa abstracts the provider behind a single `Embedder` interface.

## Providers

| Provider | Class | Status |
| --- | --- | --- |
| Hashing (dev) | `rag/embeddings/embedder.HashingEmbedder` | Deterministic, offline, no deps |
| Sentence-transformers | `rag/embeddings/embedder.SentenceTransformerEmbedder` | Real embeddings, lazy import |

`get_embedder()` returns sentence-transformers when installed and falls back to
the hashing embedder with a warning — imports never break on a cold clone.

```python
from rag.embeddings.embedder import get_embedder
from rag.embeddings.embedding_config import EmbeddingConfig

cfg = EmbeddingConfig(model_name="all-MiniLM-L6-v2", dim=384, batch_size=32)
embedder = get_embedder(cfg.model_name, cfg.dim)
vec = embedder.embed("When is the best time to visit Palolem?")
```

## Dev embedder (`HashingEmbedder`)

Pure-python, deterministic:

- Lowercases and tokenises the input.
- Hashes token n-grams (window 1..3) into `dim` buckets.
- Applies signed contributions, then L2-normalises.

It makes the pipeline *runnable and testable* offline with semantically sane
(not SOTA) behaviour. Swap in sentence-transformers for real quality numbers.

## Production options

- `all-MiniLM-L6-v2` (384-d) — fast, good baseline, small host footprint.
- `bge-small-en-v1.5` / `bge-base-en-v1.5` — better retrieval quality.
- OpenAI `text-embedding-3-small` when using the OpenAI router.

## Index fidelity

The index file name is derived from the embedder model name
(e.g. `hashing-384.npy` + `hashing-384_meta.json`). Changing the model (or the
dimension) mints a fresh index; stale indexes are simply ignored by `load_index`.

`docs/rag/retrieval.md` describes how the vectors are queried.