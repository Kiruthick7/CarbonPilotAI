from typing import Any

import structlog

try:
    from groq import AsyncGroq

    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    AsyncGroq = None  # type: ignore

from app.config import get_settings

logger = structlog.get_logger(__name__)

FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]


class LLMClient:
    def __init__(self) -> None:
        self._client: Any = None
        self._ai_ready: bool = False
        settings = get_settings()
        if GROQ_AVAILABLE and settings.groq_api_key and AsyncGroq is not None:
            try:
                self._client = AsyncGroq(api_key=settings.groq_api_key)
                self._ai_ready = True
            except Exception as e:
                logger.warning("groq_init_failed", error=str(e))
                self._client = None
                self._ai_ready = False
        else:
            self._client = None
            self._ai_ready = False

    @property
    def ai_ready(self) -> bool:
        return self._ai_ready

    @property
    def client(self) -> Any:
        return self._client

    async def create_completion_with_fallback(self, **kwargs: Any) -> Any:
        last_exc = None
        for model in FALLBACK_MODELS:
            try:
                kwargs["model"] = model
                return await self._client.chat.completions.create(**kwargs)
            except Exception as exc:
                last_exc = exc
                logger.warning("agent_model_fallback", model=model, error=str(exc))
                continue
        if last_exc:
            raise last_exc
        raise RuntimeError("No models available in FALLBACK_MODELS")
