"""Shared constants for the backend."""

from __future__ import annotations

API_PREFIX = "/api"
SERVICE_NAME = "RAGInGoa"
SERVICE_VERSION = "1.0.0"

ROUTERS = ("dev", "whisper", "openai", "chromadb", "milvus", "qdrant")

PIPELINE_STAGES = ("stt", "retrieval", "generation", "guardrails")

MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB
SUPPORTED_AUDIO_TYPES = {"audio/wav", "audio/webm", "audio/mp3", "audio/ogg", "audio/mpeg"}

DEV_TRANSCRIPT = "What is the best time to visit Palolem in Goa?"

GUARDRAIL_NAMES = ("safety", "relevance", "grounding", "refusal")

BENCHMARK_REPORT_PATH = "backend/benchmark_results/last_run.json"

SYSTEM_STATUS_OK = "ONLINE"
SYSTEM_STATUS_DEGRADED = "DEGRADED"
SYSTEM_STATUS_OFFLINE = "OFFLINE"

DEMO_QUERIES = [
    "What is the best time to visit Palolem in Goa?",
    "What food should I try while in Goa?",
    "How do I get to Dudhsagar Falls from Panaji?",
    "Where is the Latin Quarter of Panaji?",
    "Which churches in Old Goa are worth visiting?",
]

__all__ = [
    "API_PREFIX",
    "SERVICE_NAME",
    "SERVICE_VERSION",
    "ROUTERS",
    "PIPELINE_STAGES",
    "MAX_AUDIO_BYTES",
    "SUPPORTED_AUDIO_TYPES",
    "DEV_TRANSCRIPT",
    "GUARDRAIL_NAMES",
    "BENCHMARK_REPORT_PATH",
    "SYSTEM_STATUS_OK",
    "SYSTEM_STATUS_DEGRADED",
    "SYSTEM_STATUS_OFFLINE",
    "DEMO_QUERIES",
]