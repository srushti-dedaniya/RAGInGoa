# Chunking Strategies

Chunking decides the granularity of retrieval. The right chunk size is a
trade-off between *precision* (small chunks → fewer irrelevant tokens in
context) and *recall* (large chunks → more chance the answer span is inside).

All strategies are implemented in `rag/chunking/` and share one interface:

```python
from rag.chunking.chunk_manager import ChunkManager

manager = ChunkManager("sentence", {"size": 500, "overlap": 80})
chunks = manager.split(read_data("rag/data/samples/sample_goa_docs.jsonl"))
```

## 1. Fixed-size (`fixed`)

Window + overlap. Cheap, predictable, but can tear sentences mid-thought.

- **Pros:** constant size bounds on context; trivial to reason about.
- **Cons:** boundary sentences lose context unless overlap is tuned.

## 2. Sentence-based (`sentence`) — *default*

Splits on sentence boundaries and packs whole sentences until the size budget.

- **Pros:** linguistically whole chunks; citations stay readable; retrieval
  picks out self-contained units.
- **Cons:** variable lengths.

## 3. Semantic (`semantic`)

Breaks where lexical coherence between consecutive sentences drops below a
threshold — a deterministic stand-in for embedding-based segmentation.

- **Pros:** topic-aligned chunks without needing a model.
- **Cons:** lexical similarity is a weak proxy for topic coherence.

## 4. Metadata-aware (`metadata`)

Decorates any strategy with title/source prefixes and refuses to split headings.

- **Pros:** every chunk is self-describing; retrieved slices are resolvable.
- **Cons:** prefix tokens consume context budget.

## Empirical results (sample corpus, dev embedder)

| Strategy | chunks | avg len | query hit rate @2 |
| --- | --- | --- | --- |
| fixed | 9 | 308 | 0.67 |
| sentence | 9 | 308 | 0.67 |
| semantic | 18 | 86 | 0.67 |

Run `python rag/experiments/chunking_comparison.py` to reproduce.

## Tuning guidance

- Start at **size 500 / overlap 80 (sentence)**.
- For very dense documents, drop size to 300–400.
- For Q&A over short facts, sentence-based at 300 works best.
- Re-evaluate with `rag/evaluation/retrieval_eval.py` (hit@k, MRRT).