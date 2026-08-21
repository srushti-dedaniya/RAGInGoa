"""RAG service — high-level wrapper exposing query, audio and health ops."""

from __future__ import annotations

import time

from ..config.constants import (
    SERVICE_NAME,
    SERVICE_VERSION,
    SYSTEM_STATUS_DEGRADED,
    SYSTEM_STATUS_OK,
)
from ..config.settings import Settings
from ..harness.pipeline import Pipeline


class RAGService:
    """Facade over the pipeline used by the HTTP routes."""

    def __init__(self, settings: Settings, pipeline: Pipeline) -> None:
        self.settings = settings
        self.pipeline = pipeline
        self._started = time.monotonic()

    def query(self, text: str, top_k: int | None = None, language_code: str = "en-IN") -> dict:
        result = self.pipeline.run_text(text, top_k=top_k, language_code=language_code)
        return self.pipeline.to_response_dict(result)

    def audio_query(
        self, audio_bytes: bytes, filename: str, top_k: int | None = None,
        language_code: str | None = None, content_type: str | None = None,
    ) -> dict:
        result = self.pipeline.run_audio(
            audio_bytes, filename, top_k=top_k,
            language_code=language_code, content_type=content_type,
        )
        return self.pipeline.to_response_dict(result)

    def transcribe(
        self, audio_bytes: bytes, filename: str,
        language_code: str | None = None, content_type: str | None = None,
    ) -> dict:
        return self.pipeline.stt.transcribe(audio_bytes, filename, language_code, content_type)

    def benchmark(self, queries: list[str] | None, top_k: int | None) -> dict:
        from rag.benchmarking.benchmark import run_benchmark

        search_top_k = top_k or self.settings.BENCHMARK_TOP_K
        report = run_benchmark(
            queries=queries, top_k=search_top_k, query_count=100,
            include_generation=True, pipeline=self.pipeline,
        )
        report["engine_stt"] = self.settings.STT_ROUTER
        report["engine_llm"] = self.settings.LLM_ROUTER
        return report

    def health(self) -> dict:
        error = None
        try:
            ready = self.pipeline.retrieval.is_ready()
        except Exception as exc:  # readiness must remain observable when index is absent
            ready = False
            error = str(exc)
        status = SYSTEM_STATUS_OK if ready else SYSTEM_STATUS_DEGRADED
        return {
            "service": SERVICE_NAME,
            "status": status,
            "version": SERVICE_VERSION,
            "uptime_seconds": round(time.monotonic() - self._started, 1),
            "routers": {
                "stt": self.settings.STT_ROUTER,
                "llm": self.settings.LLM_ROUTER,
                "vector_db": self.settings.VECTOR_DB_ROUTER,
            },
            "index_size": self.pipeline.retrieval.index_size() if ready else 0,
            "ready": ready,
            **({"detail": error} if error else {}),
        }


__all__ = ["RAGService"]
