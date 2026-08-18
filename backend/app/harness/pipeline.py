"""Pipeline — orchestrates STT → retrieve → generate → guardrails."""

from __future__ import annotations

import time

from ..config.constants import PIPELINE_STAGES
from ..config.settings import Settings
from .error_handler import PipelineError, guard_stage, handle
from .retry import RetryPolicy
from .schemas import PipelineResult, StageResult
from ..guardrails.safety import safety_check


class Pipeline:
    """Composes the services into a single instrumented query turn."""

    def __init__(self, settings: Settings, stt, retrieval, generation, guardrails) -> None:
        self.settings = settings
        self.stt = stt
        self.retrieval = retrieval
        self.generation = generation
        self.guardrails = guardrails
        self.retry = RetryPolicy(max_attempts=2, exceptions=(TimeoutError, ConnectionError))

    # --- stage steps (each guard_stage'd) ---

    @guard_stage("stt")
    def _stt_step(
        self, audio_bytes: bytes, filename: str,
        language_code: str | None = None, content_type: str | None = None,
    ) -> dict:
        return self.stt.transcribe(audio_bytes, filename, language_code, content_type)

    @guard_stage("retrieval")
    def _retrieval_step(self, query: str, top_k: int | None) -> tuple[dict, list[dict]]:
        details = self.retrieval.details(query, top_k=top_k)
        results = details["results"]
        threshold = self.settings.SCORE_THRESHOLD
        if threshold > 0:
            results = [r for r in results if r.get("score", 0) >= threshold]
        return details, results

    @guard_stage("generation")
    def _generation_step(self, query: str, context: list[dict], language_code: str) -> dict:
        return self.retry.run(
            lambda: self.generation.generate(query, context, language_code), stage="generation"
        )

    @guard_stage("guardrails")
    def _guardrails_step(self, query: str, context: list[dict], answer: str) -> dict:
        return self.guardrails.evaluate(query, context, answer)

    # --- public flows ---

    def run_text(self, query: str, top_k: int | None = None, language_code: str = "en-IN") -> PipelineResult:
        return self._execute(query, transcript=None, top_k=top_k, language_code=language_code)

    def run_audio(
        self, audio_bytes: bytes, filename: str = "", top_k: int | None = None,
        language_code: str | None = None, content_type: str | None = None,
    ) -> PipelineResult:
        stt_result = self._stt_step(audio_bytes, filename, language_code, content_type)
        query = stt_result["transcript"]
        return self._execute(
            query, transcript=stt_result, top_k=top_k,
            language_code=language_code or self.settings.SARVAM_LANGUAGE_CODE,
        )

    def _execute(
        self, query: str, transcript: dict | None, top_k: int | None, language_code: str
    ) -> PipelineResult:
        result = PipelineResult(query=query)
        result.engine.update({
            "stt": self.settings.STT_ROUTER,
            "llm": (
                f"{self.settings.LLM_ROUTER}/{self.settings.LLM_MODEL}"
                if self.settings.LLM_ROUTER.lower() != "dev"
                else "test-extractive"
            ),
            "vector_db": "FAISS",
            "embedding": self.retrieval.embedder.model_name(),
        })
        threshold_total = time.perf_counter()

        transcript = transcript or {"transcript": query, "latency_ms": 0.0, "engine": self.settings.STT_ROUTER}
        result.engine["stt"] = transcript.get("engine", self.settings.STT_ROUTER)
        result.latency_breakdown["stt"] = transcript.get("latency_ms", 0.0)

        safety = safety_check(query)
        if not safety.passed:
            result.answer = "I can’t help with that request."
            result.guardrails = [safety.as_dict()]
            result.latency_breakdown.update({"retrieval": 0.0, "generation": 0.0, "guardrails": 0.0,
                                             "total": round((time.perf_counter()-threshold_total)*1000, 2)})
            return result

        # retrieval
        r_start = time.perf_counter()
        details, sources = self._retrieval_step(query, top_k)
        result.latency_breakdown["retrieval"] = round((time.perf_counter() - r_start) * 1000, 2)
        result.engine["vector_db"] = details.get("engine", self.settings.VECTOR_DB_ROUTER)
        result.engine["embedding"] = self.retrieval.embedder.model_name()
        result.sources = sources
        result.intermediate["transcript"] = transcript.get("transcript", query)
        result.intermediate["retrieved_count"] = len(sources)
        result.intermediate["retrieval_top_k"] = len(sources)
        result.stages.append(StageResult(name="retrieval", ok=True, latency_ms=result.latency_breakdown["retrieval"]))

        if not sources:
            result.answer = self._insufficient_answer(language_code)
            result.guardrails = [{"name": "relevance", "passed": False,
                                  "reason": "no result met the similarity threshold", "score": 0.0}]
            result.latency_breakdown.update({"generation": 0.0, "guardrails": 0.0,
                                             "total": round((time.perf_counter()-threshold_total)*1000, 2)})
            return result

        # generation
        g_start = time.perf_counter()
        gen = self._generation_step(query, sources, language_code)
        result.latency_breakdown["generation"] = round((time.perf_counter() - g_start) * 1000, 2)
        result.engine["llm"] = gen.get("provider", self.settings.LLM_ROUTER)
        result.answer = gen["answer"]
        result.stages.append(StageResult(name="generation", ok=True, latency_ms=result.latency_breakdown["generation"]))

        # guardrails
        gr_start = time.perf_counter()
        gr = self._guardrails_step(query, sources, result.answer)
        result.latency_breakdown["guardrails"] = round((time.perf_counter() - gr_start) * 1000, 2)
        result.guardrails = gr.get("checks", [])
        result.stages.append(StageResult(name="guardrails", ok=gr.get("passed", True), latency_ms=result.latency_breakdown["guardrails"]))

        result.grounded = gr.get("passed", False)
        if not result.grounded:
            result.answer = self._insufficient_answer(language_code)
        result.latency_breakdown["total"] = round((time.perf_counter() - threshold_total) * 1000, 2)
        return result

    @staticmethod
    def _insufficient_answer(language_code: str) -> str:
        return {
            "hi-IN": "उपलब्ध स्रोतों में इस प्रश्न का पर्याप्त उत्तर नहीं मिला।",
            "mr-IN": "उपलब्ध स्रोतांमध्ये या प्रश्नाचे पुरेसे उत्तर मिळाले नाही.",
        }.get(language_code, "The available sources do not contain enough information to answer this question.")

    def to_response_dict(self, result: PipelineResult) -> dict:
        guard = {"passed": all(s.ok for s in result.stages if s.name == "guardrails") or True, "checks": result.guardrails}
        guard_passed = all(c.get("passed") for c in guard["checks"])
        return {
            "success": True, "query": result.query,
            "answer": result.answer,
            "sources": result.sources,
            "grounded": result.grounded,
            "latency_ms": result.latency_breakdown.get("total", 0.0),
            "guardrails": {"passed": guard_passed, "checks": result.guardrails},
            "latency_breakdown": result.latency_breakdown,
            "engine": result.engine,
            "intermediate": result.intermediate,
            "warnings": result.warnings,
        }


__all__ = ["Pipeline"]
