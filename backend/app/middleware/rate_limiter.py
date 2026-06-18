"""
middleware/rate_limiter.py
Sliding window rate limiter using in-process state.
Works correctly on Cloud Run because each instance is single-process.
For multi-instance production scale, swap _store for a Redis client.
"""

from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)


ROUTE_LIMITS: dict[str, tuple[int, int]] = {
    "/v1/chat": (20, 60),
    "/v1/calculate": (60, 60),
    "/v1/simulate": (60, 60),
    "/v1/actions": (30, 60),
}


class SlidingWindowRateLimiter(BaseHTTPMiddleware):
    """
    Per-IP sliding window rate limiter.
    IP is SHA-256 hashed before storage — never stored raw.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._windows: dict[str, list[float]] = defaultdict(list)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path
        limit_cfg = self._match_limit(path)
        if limit_cfg is None:
            return await call_next(request)

        max_req, window = limit_cfg
        ip_hash = self._hash_ip(request.client.host if request.client else "unknown")
        key = f"ratelimit:{ip_hash}:{path}"

        now_mono = time.monotonic()
        self._windows[key] = [t for t in self._windows[key] if now_mono - t < window]

        if len(self._windows[key]) >= max_req:
            oldest = self._windows[key][0]
            retry_after = max(1, int(window - (now_mono - oldest)) + 1)
            logger.warning(
                "rate_limit_hit_memory", ip_hash=ip_hash, path=path, retry_after=retry_after
            )
            return JSONResponse(
                status_code=429,
                content={
                    "code": "RATE_LIMITED",
                    "retry_after": retry_after,
                    "message": "Too many requests",
                },
                headers={"Retry-After": str(retry_after)},
            )

        self._windows[key].append(now_mono)
        return await call_next(request)

    @staticmethod
    def _match_limit(path: str) -> tuple[int, int] | None:
        for prefix, cfg in ROUTE_LIMITS.items():
            if path.startswith(prefix):
                return cfg
        return None

    @staticmethod
    def _hash_ip(ip: str) -> str:
        return hashlib.sha256(ip.encode()).hexdigest()[:16]
