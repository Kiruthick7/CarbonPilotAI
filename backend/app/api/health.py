"""
api/health.py
Lightweight health check endpoint for Cloud Run liveness probes.
"""

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/health", tags=["ops"])
async def health_check() -> dict:
    """
    Returns service health. Used by Cloud Run readiness probes.
    Does NOT check AI connectivity — keeps probe fast and cheap.
    """
    settings = get_settings()
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.environment,
    }
