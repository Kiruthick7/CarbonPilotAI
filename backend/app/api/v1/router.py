"""
api/v1/router.py
Aggregates all v1 route modules under /v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1 import actions, calculate, chat, ocr, simulate

router = APIRouter(prefix="/v1")

router.include_router(chat.router)
router.include_router(calculate.router)
router.include_router(simulate.router)
router.include_router(actions.router)
router.include_router(ocr.router)
