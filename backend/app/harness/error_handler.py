"""Error handling — structured, stage-aware failures."""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Raised when a pipeline stage fails with a known HTTP status."""

    def __init__(self, stage: str, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.stage = stage
        self.message = message
        self.status_code = status_code


def handle(error: BaseException) -> dict[str, Any]:
    """Normalise any exception into an API-friendly error dict."""
    if isinstance(error, PipelineError):
        status = error.status_code
        if error.stage == "stt":
            # Keep provider/decode details in server logs, never in the API response.
            status = 422
            message = "Couldn't understand the recording. Please try again."
            code = "speech_not_understood"
        else:
            message = error.message
            code = "pipeline_error"
    elif isinstance(error, ValueError):  # bad input before processing
        status = 400
        message = str(error)
    else:
        status = 500
        message = "internal pipeline error"
        code = "internal_error"
    if not isinstance(error, PipelineError):
        code = "invalid_request" if isinstance(error, ValueError) else code
    logger.exception("pipeline error: %s", getattr(error, "message", str(error)))
    return {
        "error": True,
        "message": message,
        "status_code": status,
        "code": code,
        "detail": message,
    }


def guard_stage(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator: catch exceptions in a stage, log and raise PipelineError."""

    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except PipelineError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise PipelineError(stage=name, message=f"'{name}' stage failed: {exc}") from exc

        return wrapper

    return deco


__all__ = ["PipelineError", "handle", "guard_stage"]
