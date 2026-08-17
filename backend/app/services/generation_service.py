"""Generation service — grounded answer from retrieved chunks."""

from __future__ import annotations

import logging
import time

from ..config.settings import Settings

logger = logging.getLogger(__name__)


class GenerationService:
    """Produces a grounded answer. Dev router cites the retrieved sources."""

    def __init__(self, settings: Settings) -> None:
        self.router = settings.LLM_ROUTER.lower()

    def generate(self, query: str, context: list[dict]) -> dict:
        started = time.perf_counter()
        if self.router == "openai":
            try:
                answer = self._openai_generate(query, context)
                provider = "openai"
            except Exception as exc:  # noqa: BLE001
                logger.warning("openai generation failed (%s); using dev generator", exc)
                answer, provider = self._dev_generate(query, context), "dev"
        else:
            answer, provider = self._dev_generate(query, context), "dev"
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "answer": answer,
            "provider": provider,
            "model": "dev-grounded" if provider == "dev" else "gpt-4o-mini",
            "latency_ms": latency_ms,
            "tokens_used": len(answer.split()) * 2,
        }

    def _dev_generate(self, query: str, context: list[dict]) -> str:
        if not context:
            return (
                "I couldn't find enough context in the index to answer that safely. "
                "Try rephrasing the question."
            )
        seen: set[str] = set()
        points: list[str] = []
        for chunk in context[:3]:
            text = (chunk.get("text") or "").strip()
            title = chunk.get("metadata", {}).get("title")
            key = title or chunk.get("chunk_id", "")
            if not text or text in seen:
                continue
            seen.add(key)
            points.append(f"{text[:300].rstrip()}")
        body = " ".join(points)
        lead = self._lead(query)
        return (
            f"{lead}\n\n{body}\n\n" + "References: " + ", ".join(
                f"[Source: {p.get('metadata', {}).get('title', p.get('chunk_id', ''))}]"
                for p in context[:3] if p.get("metadata", {}).get("title")
            )
        )

    def _lead(self, query: str) -> str:
        return f"Based on the retrieved Goa context, here is what I found about “{query}”."

    def _openai_generate(self, query: str, context: list[dict]) -> str:
        from openai import OpenAI  # optional dep
        from ..config.settings import get_settings

        settings = get_settings()
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        passages = [
            f"[Source: {c.get('metadata', {}).get('title', 'unknown')}]\n{c.get('text', '')}"
            for c in context
        ]
        system = (
            "You are a grounded answer assistant. Answer ONLY from the sources below. "
            "Cite sources inline as [Source: title]. If the sources cannot answer, say so."
        )
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Question:\n{query}\n\nSources:\n" + "\n\n".join(passages)},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""


__all__ = ["GenerationService"]