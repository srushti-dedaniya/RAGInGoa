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
    STT_ROUTER: str = "dev"
    LLM_ROUTER: str = "dev"
    VECTOR_DB_ROUTER: str = "dev"

    # Providers
    OPENAI_API_KEY: str = ""
    VECTOR_DB_URL: str = "http://localhost:19530"
    VECTOR_DB_COLLECTION: str = "ragingoa"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # Chunking
    CHUNK_STRATEGY: str = "sentence"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 80

    # Retrieval / generation
    TOP_K: int = 4
    BENCHMARK_TOP_K: int = 4
    SCORE_THRESHOLD: float = 0.0
    RERANK: bool = False

    # Paths
    INDEX_DIR: str = "rag/vector_db/index"
    PROCESSED_DATA_DIR: str = "rag/data/processed"
    SAMPLE_DATA_PATH: str = "rag/data/samples/sample_goa_docs.jsonl"

    # HTTP
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    PORT: int = 8000

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def index_path(self) -> Path:
        return REPO_ROOT / self.INDEX_DIR

    @property
    def processed_path(self) -> Path:
        return REPO_ROOT / self.PROCESSED_DATA_DIR

    @property
    def sample_data_path(self) -> Path:
        return REPO_ROOT / self.SAMPLE_DATA_PATH


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings", "REPO_ROOT"]