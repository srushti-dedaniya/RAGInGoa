"""Request logging middleware."""

from __future__ import annotations

import logging
import time

logger = logging.getLogger("ragingoa.access")


class RequestLoggingMiddleware:
    """Logs method, path, status and duration per request."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:  # noqa: ANN001
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        status_holder: dict = {"status": 500}

        async def send_wrapper(message) -> None:  # noqa: ANN001
            if message["type"] == "http.response.start":
                status_holder["status"] = message.get("status", 500)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info(
                "%s %s -> %s in %.2fms",
                scope.get("method", "?"),
                scope.get("path", scope.get("route", "?")),
                status_holder["status"],
                duration_ms,
            )


__all__ = ["RequestLoggingMiddleware"]