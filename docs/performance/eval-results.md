# Retrieval Evaluation Results

Produced by `rag/evaluation/retrieval_eval.py` against the tagged queries in
`rag/evaluation/test_queries.json` (10 queries, `k = 4`, sentence chunking).

## Headline metrics

| Metric | Score |
| --- | ---: |
| hit@4 | 1.00 |
| recall@4 | 1.00 |
| MRRT (mean reciprocal retrieval rank) | 1.00 |
| top-1 accuracy | 100% (10/10) |

Every tagged query retrieved its expected topic document within the top 4, and
in every case at rank 1.

## Per-query breakdown

| Query | hit@4 | recall@4 | MRRT | Rank 1 |
| --- | :---: | :---: | :---: | :---: |
| When is the best time to visit Palolem? | ✓ | 1.00 | 1.00 | ✓ |
| What food should I try in Goa? | ✓ | 1.00 | 1.00 | ✓ |
| How do I get to Dudhsagar Falls? | ✓ | 1.00 | 1.00 | ✓ |
| Where is the Latin Quarter of Panaji? | ✓ | 1.00 | 1.00 | ✓ |
| Which church holds the remains of Saint Francis Xavier? | ✓ | 1.00 | 1.00 | ✓ |
| What is the cheapest way to get around Goa? | ✓ | 1.00 | 1.00 | ✓ |
| Where can I see turtle nesting beaches? | ✓ | 1.00 | 1.00 | ✓ |
| When do the night markets in Goa peak? | ✓ | 1.00 | 1.00 | ✓ |
| Are there evening cruises on the Mandovi? | ✓ | 1.00 | 1.00 | ✓ |
| What is bebinca? | ✓ | 1.00 | 1.00 | ✓ |

Eval wall time: ~130 ms for all 10 queries (index warm, CPU laptop).

## Setup

- Embedder: `all-MiniLM-L6-v2` (384-d, sentence-transformers), L2-normalised
- Index: FAISS `IndexFlatIP` over sentence chunks of the sample corpus
- Relevance judgement: chunk matches the query's `expected_topic` metadata or
  contains a hint phrase from `test_queries.json`

## Caveats

The sample corpus is small (one document per topic), so perfect scores are
expected and should be read as a **sanity floor**, not production evidence.
Re-run this suite after any change to chunking, embeddings, or the corpus:

```bash
python -m rag.evaluation.retrieval_eval 4
```

For harder evaluation at scale, point the harness at the full MSMARCO-XI
corpus with additional tagged queries.
