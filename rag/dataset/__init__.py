"""Dataset acquisition and cleaning for RAGInGoa."""

from rag.dataset.loader import read_data
from rag.dataset.cleaner import clean_text

__all__ = ["read_data", "clean_text"]