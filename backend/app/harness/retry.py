"""Retry policy with exponential backoff and jitter."""

from __future__ import annotations

import logging
import random
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


class RetryPolicy:
    """Retries ``fn`` up to ``max_attempts`` times on listed exceptions.

    Backoff grows ``base * 2 ** attempt`` with ±33% jitter so convoys break up.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay_ms: float = 200.0,
        exceptions: tuple[type[BaseException], ...] = (ConnectionError, TimeoutError),
    ) -> None:
        self.max_attempts = max(1, max_attempts)
        self.base_delay_ms = base_delay_ms
        self.exceptions = exceptions

    def _delay(self, attempt: int) -> float:
        backoff = self.base_delay_ms * (2 ** max(0, attempt - 1))
        return backoff * (0.67 + random.random() * 0.66)

    def run(self, fn: Callable[[], Any], stage: str = "") -> Any:
        last: BaseException | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return fn()
            except self.exceptions as exc:  # noqa: PERF203
                last = exc
                if attempt == self.max_attempts:
                    break
                delay = self._delay(attempt)
                logger.warning(
                    "retrying %s (attempt %d/%d) after %.0fms: %s",
                    stage or "call",
                    attempt,
                    self.max_attempts,
                    delay,
                    exc,
                )
                time.sleep(delay / 1000.0)
        raise RuntimeError(f"{stage or 'call'} failed after retries") from last


__all__ = ["RetryPolicy"]