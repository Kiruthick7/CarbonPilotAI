"""Application configuration loaded from environment variables.

Uses Pydantic-Settings for validation and type coercion. Access the singleton
via ``get_settings()`` — it is cached with ``lru_cache`` so the environment is
only read once per process.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration for the CarbonPilot AI backend.

    Values are read from environment variables (case-insensitive) and, when
    running locally, from a ``.env`` file in the backend directory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )




    groq_api_key: str = Field(
        ...,
        description="Groq API key — obtain from https://console.groq.com/keys",
    )




    environment: Literal["development", "production"] = Field(
        default="development",
        description="Runtime environment. Controls log formatting and debug features.",
    )
    log_level: str = Field(
        default="INFO",
        description="Minimum structlog log level.",
    )
    app_version: str = Field(
        default="1.0.0",
        description="Semantic version surfaced in /health and OpenAPI docs.",
    )




    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed frontend origins.",
    )

    # Removed database_url as application is stateless.




    # Removed rate_limit_chat, rate_limit_window_seconds, and redis_url as they are unused or unneeded.




    @field_validator("cors_origins")
    @classmethod
    def _cors_not_empty(cls, v: str) -> str:
        """Ensure at least one origin is specified."""
        if not v.strip():
            raise ValueError("CORS_ORIGINS must not be empty.")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a deduplicated list of stripped strings."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Return ``True`` when running in a production environment."""
        return self.environment == "production"




@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Call ``get_settings.cache_clear()`` in tests to reset between runs.
    """
    return Settings()  # type: ignore[call-arg]
