"""Exception handling middleware — JSON errors for pipeline failures."""

from __future__ import annotations

import json
import logging

from starlette.responses import JSONResponse

from ..harness.error_handler import PipelineError, handle

logger = logging.getLogger("ragingoa.error")


class PipelineExceptionMiddleware:
    """Converts PipelineError / ValueError / generic failures to JSON errors."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:  # noqa: ANN001
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_catch(message) -> None:  # noqa: ANN001
            await send(message)

        try:
            await self.app(scope, receive, send_catch)
        except PipelineError as exc:
            await self._error_response(scope, receive, send, handle(exc))
        except ValueError as exc:
            await self._error_response(scope, receive, send, handle(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("unhandled error")
            await self._error_response(scope, receive, send, handle(exc))

    async def _error_response(self, scope, receive, send, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": int(payload.get("status_code", 500)),
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send({"type": "http.response.body", "body": body})


__all__ = ["PipelineExceptionMiddleware"]