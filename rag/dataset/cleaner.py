"""Text cleaning utilities for the corpus pipeline."""

from __future__ import annotations

import re

_WS_PATTERN = re.compile(r"\s+")
_CTRL_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(text: str | None) -> str:
    """Normalise whitespace, drop control chars and strip markdown/HTML noise."""
    if not text:
        return ""
    text = _CTRL_PATTERN.sub(" ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = _WS_PATTERN.sub(" ", text)
    return text.strip()


def normalise_metadata(metadata: dict) -> dict:
    """Return metadata with string-coerced, stripped values."""
    cleaned: dict = {}
    for key, value in metadata.items():
        if isinstance(value, str):
            cleaned[key] = value.strip()
        else:
            cleaned[key] = value
    return cleaned


__all__ = ["clean_text", "normalise_metadata"]