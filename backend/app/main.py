"""RAGInGoa backend entrypoint.

Wires routers, services and middleware, then serves the FastAPI app.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.constants import API_PREFIX, SERVICE_NAME, SERVICE_VERSION
from .config.settings import Settings, get_settings
from .harness.pipeline import Pipeline
from .middleware.error import PipelineExceptionMiddleware
from .middleware.logging import RequestLoggingMiddleware
from .routes import api_router
from .services import (
    GenerationService,
    GuardrailService,
    RAGService,
    RetrievalService,
    STTService,
    TTSService,
)

logger = logging.getLogger("ragingoa")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

from rag.embeddings.embedder import get_embedder  # noqa: E402


class Services:
    """Shared, lazily-built service container."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedder = get_embedder(model_name=settings.EMBEDDING_MODEL, dim=settings.EMBEDDING_DIM)
        self.stt = STTService(settings)
        self.tts = TTSService(settings)
        self.retrieval = RetrievalService(settings, self.embedder)
        self.generation = GenerationService(settings)
        self.guardrails = GuardrailService(settings, embedder=self.embedder)
        self.pipeline = Pipeline(
            settings,
            self.stt,
            self.retrieval,
            self.generation,
            self.guardrails,
        )
        self.rag = RAGService(settings, self.pipeline)

    def query(self, text: str, top_k: int | None = None, language_code: str = "en-IN") -> dict:
        return self.rag.query(text, top_k=top_k, language_code=language_code)

    def audio_query(
        self, audio_bytes: bytes, filename: str, top_k: int | None = None,
        language_code: str | None = None, content_type: str | None = None,
    ) -> dict:
        return self.rag.audio_query(
            audio_bytes, filename, top_k=top_k,
            language_code=language_code, content_type=content_type,
        )

    def transcribe(
        self, audio_bytes: bytes, filename: str,
        language_code: str | None = None, content_type: str | None = None,
    ) -> dict:
        return self.rag.transcribe(audio_bytes, filename, language_code, content_type)

    def benchmark(self, queries: list[str] | None, top_k: int | None) -> dict:
        return self.rag.benchmark(queries, top_k)

    def synthesize(self, text: str, language_code: str) -> bytes:
        return self.tts.synthesize(text, language_code)

    def health(self) -> dict:
        return self.rag.health()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.services = Services(settings)
    app.state.services.retrieval.is_ready()
    app.state.services.embedder.embed("RAGInGoa startup warmup")
    app.state.benchmark_report = {}
    logger.info(
        "RAGInGoa online: stt=%s llm=%s vdb=%s embed=%s",
        settings.STT_ROUTER,
        settings.LLM_ROUTER,
        settings.VECTOR_DB_ROUTER,
        app.state.services.embedder.model_name(),
    )
    yield


app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    description="Voice → RAG → Answer. Speak a question, retrieve the signal, get a grounded answer.",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(PipelineExceptionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=API_PREFIX)


@app.get("/")
async def root() -> dict:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "tagline": "Less noise. More signal.",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/health", include_in_schema=False)
async def root_health() -> dict:
    return app.state.services.health()


__all__ = ["app"]
