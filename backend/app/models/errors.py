"""Pydantic v2 models for standardised API error responses.

All API endpoints return ``ErrorResponse`` on failure. The ``ErrorCode`` enum
ensures clients can programmatically distinguish error conditions without
parsing free-form message strings.
"""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """Python 3.9-compatible StrEnum substitute."""

    pass


from pydantic import BaseModel, Field


class ErrorCode(StrEnum):
    """Stable machine-readable error codes returned in ``ErrorResponse.code``.

    Codes are grouped by prefix:
    - ``AUTH_*``     — authentication and authorisation failures
    - ``RATE_*``     — rate limiting
    - ``VAL_*``      — input validation failures
    - ``CALC_*``     — carbon calculation engine errors
    - ``AI_*``       — Gemini / LLM integration errors
    - ``DATA_*``     — data-loading and reference-data errors
    - ``SYS_*``      — unexpected internal server errors
    """

    AUTH_MISSING_KEY = "AUTH_MISSING_KEY"
    AUTH_INVALID_KEY = "AUTH_INVALID_KEY"

    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    VAL_INVALID_PROFILE = "VAL_INVALID_PROFILE"
    VAL_INVALID_INVENTORY = "VAL_INVALID_INVENTORY"
    VAL_INVALID_SCENARIO = "VAL_INVALID_SCENARIO"
    VAL_INVALID_REQUEST = "VAL_INVALID_REQUEST"
    VAL_COUNTRY_CODE_UNKNOWN = "VAL_COUNTRY_CODE_UNKNOWN"
    VAL_EMPTY_MESSAGES = "VAL_EMPTY_MESSAGES"

    CALC_OVERFLOW = "CALC_OVERFLOW"
    CALC_MISSING_FACTOR = "CALC_MISSING_FACTOR"
    CALC_NEGATIVE_RESULT = "CALC_NEGATIVE_RESULT"

    AI_UPSTREAM_ERROR = "AI_UPSTREAM_ERROR"
    AI_CONTENT_BLOCKED = "AI_CONTENT_BLOCKED"
    AI_TIMEOUT = "AI_TIMEOUT"
    AI_QUOTA_EXCEEDED = "AI_QUOTA_EXCEEDED"
    AI_INVALID_TOOL_CALL = "AI_INVALID_TOOL_CALL"

    DATA_LOAD_FAILURE = "DATA_LOAD_FAILURE"
    DATA_MALFORMED = "DATA_MALFORMED"
    DATA_VERSION_MISMATCH = "DATA_VERSION_MISMATCH"

    SYS_INTERNAL_ERROR = "SYS_INTERNAL_ERROR"
    SYS_NOT_IMPLEMENTED = "SYS_NOT_IMPLEMENTED"
    SYS_SERVICE_UNAVAILABLE = "SYS_SERVICE_UNAVAILABLE"


class ErrorResponse(BaseModel):
    """Standardised error envelope returned by all API error handlers.

    ``fallback_mode`` is ``True`` when the system has degraded gracefully and
    the client may retry with reduced functionality rather than failing hard.
    ``retry_after`` (seconds) is populated for rate-limit and upstream-timeout
    errors to guide client back-off.
    """

    code: ErrorCode = Field(..., description="Stable machine-readable error code.")
    message: str = Field(
        ..., min_length=1, max_length=512, description="Human-readable error summary."
    )
    detail: str | None = Field(
        default=None,
        max_length=2_048,
        description="Extended technical detail, omitted in production.",
    )
    retry_after: int | None = Field(
        default=None,
        ge=1,
        le=3_600,
        description="Seconds the client should wait before retrying (rate-limit / timeout).",
    )
    fallback_mode: bool = Field(
        default=False,
        description="True when the API is operating in a gracefully degraded state.",
    )
