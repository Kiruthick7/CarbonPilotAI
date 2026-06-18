"""
middleware/correlation_id.py
Injects X-Correlation-ID into every request context and response header.
All log lines within the request automatically include the correlation ID
via structlog's context vars.
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

import structlog
import structlog.contextvars
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

HEADER_NAME = "X-Correlation-ID"


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    If the client sends X-Correlation-ID, use it (for end-to-end tracing).
    Otherwise generate a new UUID4. Echo it back in the response.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get(HEADER_NAME) or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        response = await call_next(request)
        response.headers[HEADER_NAME] = correlation_id
        return response
