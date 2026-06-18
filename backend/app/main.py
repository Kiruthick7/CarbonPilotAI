"""
main.py
FastAPI application factory.
All middleware, routers, and startup events are registered here.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Awaitable, Callable

import structlog
import structlog.contextvars
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1.router import router as v1_router
from app.config import get_settings
from app.middleware.correlation_id import CorrelationIDMiddleware
from app.middleware.rate_limiter import SlidingWindowRateLimiter

logger = structlog.get_logger(__name__)


def configure_logging(level: str = "INFO") -> None:
    """Set up structured JSON logging via structlog."""
    import logging
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer() if level == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def create_app() -> FastAPI:
    """Application factory — returns a configured FastAPI instance."""
    settings = get_settings()
    configure_logging(settings.log_level)

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app_instance: FastAPI) -> AsyncGenerator[None, None]:
        from app.dependencies import get_loader
        get_loader()
        logger.info("carbonpilot_started", version=settings.app_version, env=settings.environment)
        yield

    app = FastAPI(
        title="CarbonPilot AI",
        description="Your AI Sustainability Coach — carbon footprint calculation and personalised action planning.",
        version=settings.app_version,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
        lifespan=lifespan,
    )


    @app.middleware("http")
    async def security_headers(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response


    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(SlidingWindowRateLimiter)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    app.include_router(health_router)
    app.include_router(v1_router)

    return app


app = create_app()
