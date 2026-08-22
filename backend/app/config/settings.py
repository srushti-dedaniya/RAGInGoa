"""Application settings, loaded from environment / ``.env``."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]  # .../backend
REPO_ROOT = BACKEND_ROOT.parent  # project root (parent of backend/)


class Settings(BaseSettings):
    """Runtime configuration. Every field has a dev-friendly default."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    # Routers
    STT_ROUTER: str = "sarvam"
    LLM_ROUTER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    VECTOR_DB_ROUTER: str = "dev"

    # Providers
    OPENAI_API_KEY: str = ""
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_REASONING_EFFORT: str = ""
    SARVAM_API_KEY: str = ""
    SARVAM_STT_URL: str = "https://api.sarvam.ai/speech-to-text"
    SARVAM_STT_MODEL: str = "saaras:v3"
    SARVAM_LANGUAGE_CODE: str = "unknown"
    SARVAM_LLM_URL: str = "https://api.sarvam.ai/v1"
    SARVAM_TTS_URL: str = "https://api.sarvam.ai/text-to-speech"
    SARVAM_TTS_MODEL: str = "bulbul:v3"
    SARVAM_TTS_SPEAKER: str = "shubh"
    EXTERNAL_TIMEOUT_SECONDS: float = 20.0
    EXTERNAL_MAX_RETRIES: int = 2
    VECTOR_DB_URL: str = "http://localhost:19530"
    VECTOR_DB_COLLECTION: str = "ragingoa"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # Chunking
    CHUNKING_STRATEGY: str = "sentence"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 80

    # Retrieval / generation
    TOP_K: int = 4
    BENCHMARK_TOP_K: int = 4
    SIMILARITY_THRESHOLD: float = 0.25
    RERANK: bool = False

    # Paths
    DEFAULT_LANGUAGE: str = "en-IN"
    VECTOR_DB_PATH: str = "rag/vector_db/index/en"
    VECTOR_DB_PATH_EN: str = "rag/vector_db/index/en"
    VECTOR_DB_PATH_HI: str = "rag/vector_db/index/hi"
    VECTOR_DB_PATH_MR: str = "rag/vector_db/index/mr"
    PROCESSED_DATA_DIR: str = "rag/data/processed"
    SAMPLE_DATA_PATH: str = "rag/data/samples/sample_goa_docs.jsonl"
    DATASET_PATH: str = "rag/data/processed/msmarco_xi_en.jsonl"
    DATASET_PATH_EN: str = "rag/data/processed/msmarco_xi_en.jsonl"
    DATASET_PATH_HI: str = "rag/data/processed/msmarco_xi_hi.jsonl"
    DATASET_PATH_MR: str = "rag/data/processed/msmarco_xi_mr.jsonl"
    DATASET_NAME: str = "ai4bharat/MSMARCO-XI"
    DATASET_LANGUAGE: str = "en"
    DATASET_SPLIT: str = "validation"
    DATASET_MAX_RECORDS: int = 5000
    REQUIRE_INDEX: bool = True

    # HTTP
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:3000,http://127.0.0.1:3000"
    PORT: int = 8000

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def index_path(self) -> Path:
        return self.index_path_for("en-IN")

    def index_path_for(self, language_code: str) -> Path:
        relative = {
            "hi-IN": self.VECTOR_DB_PATH_HI,
            "mr-IN": self.VECTOR_DB_PATH_MR,
        }.get(language_code, self.VECTOR_DB_PATH_EN)
        return REPO_ROOT / relative

    @property
    def processed_path(self) -> Path:
        return REPO_ROOT / self.PROCESSED_DATA_DIR

    @property
    def sample_data_path(self) -> Path:
        return REPO_ROOT / self.SAMPLE_DATA_PATH

    @property
    def dataset_path(self) -> Path:
        return self.dataset_path_for("en-IN")

    def dataset_path_for(self, language_code: str) -> Path:
        relative = {
            "hi-IN": self.DATASET_PATH_HI,
            "mr-IN": self.DATASET_PATH_MR,
        }.get(language_code, self.DATASET_PATH_EN)
        return REPO_ROOT / relative

    @property
    def CHUNK_STRATEGY(self) -> str:  # backwards-compatible internal alias
        return self.CHUNKING_STRATEGY

    @property
    def SCORE_THRESHOLD(self) -> float:
        return self.SIMILARITY_THRESHOLD


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings", "REPO_ROOT"]
