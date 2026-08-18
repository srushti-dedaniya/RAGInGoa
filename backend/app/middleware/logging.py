"""Request logging middleware."""

from __future__ import annotations

import logging
import time
import uuid
import json

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
        request_id = str(uuid.uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        status_holder: dict = {"status": 500}

        async def send_wrapper(message) -> None:  # noqa: ANN001
            if message["type"] == "http.response.start":
                status_holder["status"] = message.get("status", 500)
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("ascii")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info(json.dumps({"request_id": request_id, "stage": "http",
                "method": scope.get("method", "?"), "path": scope.get("path", "?"),
                "status": status_holder["status"], "latency_ms": duration_ms}))


__all__ = ["RequestLoggingMiddleware"]
