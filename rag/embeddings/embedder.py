"""Embedding providers.

``get_embedder`` returns the best available provider: a torch-free ONNX Runtime
embedder when the exported model is present, otherwise sentence-transformers,
otherwise a deterministic hashing embedder so the pipeline runs offline without
breaking imports.
"""

from __future__ import annotations

import hashlib
import logging
import math
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

ONNX_DIR = Path(__file__).resolve().parent / "onnx"


class Embedder:
    """Common interface for embedding providers."""

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]

    def model_name(self) -> str:
        raise NotImplementedError


class HashingEmbedder(Embedder):
    """Deterministic, dependency-free embedder for dev mode.

    Each token contributes to several neighbouring buckets via a seeded hash in
    a sliding window (a poor-man's local hashing). The vector is L2-normalised,
    so cosine search behaves sensibly even with this weak signal.
    """

    def __init__(self, dim: int = 384, window: int = 3) -> None:
        super().__init__(dim=dim)
        self.window = max(1, int(window))

    def _tokens(self, text: str) -> list[str]:
        norm = text.lower()
        return [tok for tok in norm.split() if tok]

    def _window_hashes(self, text: str) -> list[int]:
        toks = self._tokens(text)
        if not toks:
            return []
        hashes: list[int] = []
        for i in range(len(toks)):
            for w in range(1, self.window + 1):
                if i + w > len(toks):
                    break
                grams = " ".join(toks[i : i + w])
                hashes.append(int(hashlib.sha256(grams.encode("utf-8")).hexdigest()[:8], 16))
        return hashes

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        hashes = self._window_hashes(text)
        if not hashes:
            return vec
        for h in hashes:
            base = h % self.dim
            for j in range(3):
                bucket = (base + j) % self.dim
                sign = 1.0 if ((h >> j) & 1) else -1.0
                vec[bucket] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1e-9
        return [v / norm for v in vec]

    def model_name(self) -> str:
        return f"hashing-{self.dim}"


class SentenceTransformerEmbedder(Embedder):
    """Wrapper around sentence-transformers, imported lazily."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dim: int = 384) -> None:
        super().__init__(dim=dim)
        from sentence_transformers import SentenceTransformer  # optional dep

        # The index build/setup step downloads the model. Runtime must use that
        # cached copy instead of issuing slow Hugging Face metadata requests.
        self._model = SentenceTransformer(model_name, local_files_only=True)
        self._name = model_name

    @lru_cache(maxsize=512)
    def embed(self, text: str) -> list[float]:
        return self._model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=False).tolist()

    def model_name(self) -> str:
        return self._name


class OnnxEmbedder(Embedder):
    """Torch-free embedder running the exported MiniLM graph via ONNX Runtime.

    Produces the same vectors as sentence-transformers (mean pooling over token
    embeddings + L2 normalisation), so indexes built with either provider stay
    compatible.
    """

    def __init__(
        self,
        model_dir: Path = ONNX_DIR,
        model_name: str = "all-MiniLM-L6-v2",
        dim: int = 384,
        max_length: int = 256,
    ) -> None:
        super().__init__(dim=dim)
        import onnxruntime as ort
        from tokenizers import Tokenizer

        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        self._session = ort.InferenceSession(
            str(model_dir / "model.onnx"),
            sess_options=options,
            providers=["CPUExecutionProvider"],
        )
        self._tokenizer = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        self._tokenizer.enable_truncation(max_length=max_length)
        self._tokenizer.enable_padding()
        self._name = model_name

    @staticmethod
    def _mean_pool(hidden, mask):
        import numpy as np

        mask = mask[:, :, None].astype(hidden.dtype)
        summed = (hidden * mask).sum(axis=1)
        counts = np.clip(mask.sum(axis=1), 1e-9, None)
        return summed / counts

    @lru_cache(maxsize=512)
    def embed(self, text: str) -> tuple[float, ...]:
        import numpy as np

        encoded = self._tokenizer.encode(text)
        hidden = self._session.run(
            ["last_hidden_state"],
            {
                "input_ids": np.array([encoded.ids], dtype=np.int64),
                "attention_mask": np.array([encoded.attention_mask], dtype=np.int64),
            },
        )[0]
        vector = self._mean_pool(hidden, np.array([encoded.attention_mask]))[0]
        vector = vector / (np.linalg.norm(vector) or 1e-9)
        return tuple(float(v) for v in vector)

    def embed_batch(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        import numpy as np

        if not texts:
            return []
        out: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            encoded = self._tokenizer.encode_batch(chunk)
            hidden = self._session.run(
                ["last_hidden_state"],
                {
                    "input_ids": np.array([e.ids for e in encoded], dtype=np.int64),
                    "attention_mask": np.array([e.attention_mask for e in encoded], dtype=np.int64),
                },
            )[0]
            pooled = self._mean_pool(hidden, np.array([e.attention_mask for e in encoded]))
            norms = np.linalg.norm(pooled, axis=1, keepdims=True)
            pooled = pooled / np.clip(norms, 1e-9, None)
            out.extend(row.tolist() for row in pooled)
        return out

    def model_name(self) -> str:
        return self._name


def onnx_available() -> bool:
    try:
        import onnxruntime  # noqa: F401
        from tokenizers import Tokenizer  # noqa: F401
    except ImportError:
        return False
    return (ONNX_DIR / "model.onnx").exists() and (ONNX_DIR / "tokenizer.json").exists()


@lru_cache(maxsize=4)
def get_embedder(model_name: str = "all-MiniLM-L6-v2", dim: int = 384, allow_fallback: bool = True) -> Embedder:
    """Return OnnxEmbedder when available, else sentence-transformers, else HashingEmbedder."""
    if model_name.lower() in {"dev", "hashing", "test"}:
        return HashingEmbedder(dim=dim)
    if model_name.lower() == "all-minilm-l6-v2" and onnx_available():
        logger.info("using torch-free ONNX embedder")
        return OnnxEmbedder(model_name=model_name, dim=dim)
    try:
        return SentenceTransformerEmbedder(model_name=model_name, dim=dim)
    except ImportError:  # pragma: no cover - runs only when lib missing
        if not allow_fallback:
            raise RuntimeError("sentence-transformers is required for production indexing")
        logger.warning(
            "sentence-transformers not installed; using dev HashingEmbedder(dim=%d)", dim
        )
        return HashingEmbedder(dim=dim)


__all__ = ["Embedder", "HashingEmbedder", "OnnxEmbedder", "SentenceTransformerEmbedder", "get_embedder", "onnx_available"]
