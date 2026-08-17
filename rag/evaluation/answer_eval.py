"""Answer quality evaluation.

Faithfulness is approximated with lexical overlap (a lightweight ROUGE-L-ish
proxy) and groundedness by requiring the answer to cite a source key that
appears in the retrieved context.
"""

from __future__ import annotations

import re
from collections import Counter

_PUNCT = re.compile(r"[.,;:!?\"()'\[\]]")


def tokens(text: str) -> list[str]:
    return [_PUNCT.sub("", t) for t in str(text).lower().split() if _PUNCT.sub("", t)]


def rouge_l_proxy(answer: str, context: str) -> float:
    """Fraction of answer tokens that appear in the context (token recall)."""
    a = Counter(tokens(answer))
    c = Counter(tokens(context))
    if not a:
        return 1.0
    matched = sum(min(v, c.get(k, 0)) for k, v in a.items())
    return matched / sum(a.values())


def grounding_ratio(answer: str, sources: list[dict]) -> tuple[float, list[str]]:
    """Fraction of sources whose key (title/source) is cited in the answer."""
    cited: list[str] = []
    for src in sources:
        key = src.get("metadata", {}).get("title") or src.get("metadata", {}).get("source")
        if not key:
            continue
        if key.lower() in answer.lower():
            cited.append(key)
    return (len(cited) / max(1, len(sources)), cited)


def eval_answer(answer: str, context: list[dict]) -> dict:
    """Return faithfulness, groundedness and citation diagnostics."""
    ctx_text = " ".join(c.get("text", "") for c in context)
    faithfulness = rouge_l_proxy(answer, ctx_text)
    grounded, cited = grounding_ratio(answer, context)
    return {
        "faithfulness": round(faithfulness, 4),
        "groundedness": round(grounded, 4),
        "cited_sources": cited,
        "passed": (faithfulness >= 0.25 and grounded >= 0.5),
    }


__all__ = ["eval_answer", "rouge_l_proxy", "grounding_ratio"]