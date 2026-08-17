# Guardrails

> Grounded. Or nothing.

RAG is only trustworthy if the answer can be traced to retrieved evidence.
RAGInGoa runs four guardrails on **every** query turn
(`backend/app/guardrails/`), and surfaces the results in both the API response
and the frontend dashboard.

## The four checks

| Check | Module | Question it answers |
| --- | --- | --- |
| Safety | `safety.py` | Is the query harmful? (blocklist of intents) |
| Relevance | `relevance.py` | Does the retrieved context actually relate to the query? (mean cross-similarity) |
| Grounding | `grounding.py` | Does the answer cite at least one retrieved source? |
| Refusal | `refusal.py` | Is this a prompt-injection / instruction override? |

## Order

```
safety → relevance → grounding → refusal
```

All four run independently and each returns `{name, passed, reason, score}`.
`guardrails.summarize()` flattens them into `{passed, checks}`.

## Grounding detail

The grounding check is deliberately strict:

- The answer must **cite a source key** (title/source) that exists in the
  retrieved context (substring match on the answer text).
- The dev generator always emits `[Source: <title>]` markers, so grounded
  answers pass; an answer generated without context is refused/flagged.

## Relevance detail

Relevance embeds the query and the top chunks with the shared embedder and
compares cosine similarity against `SCORE_THRESHOLD` (dev default 0.02). An
empty context is scored 0.0 and fails.

## Frontend

`frontend/src/components/Guardrails/Guardrails.jsx` renders the four checks for
the last answer: green (passed) / red (blocked) / grey (idle), with the reason
string under each check.

## Extending

Implement `check(query, context, answer=None) -> Result` in a new module,
register it in `run_all()` (`backend/app/guardrails/__init__.py`), and it flows
through the API and UI automatically.