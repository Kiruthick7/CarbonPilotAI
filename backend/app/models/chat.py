"""Pydantic v2 models for the chat interface.

These models govern request/response shapes for the streaming chat endpoint,
including message history, session management, and SSE event framing.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum


class StrEnum(str, Enum):
    """Python 3.9-compatible StrEnum substitute."""
    pass
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.models.carbon import CarbonInventory, CarbonProfilePartial


class MessageRole(StrEnum):
    """Roles that can appear in the conversation history."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class StreamEventType(StrEnum):
    """Discriminator for Server-Sent Event frames emitted by the chat stream."""

    TEXT_DELTA = "text_delta"
    TOOL_CALL = "tool_call"
    ERROR = "error"
    DONE = "done"







class ChatMessage(BaseModel):
    """A single message in the conversation history.

    ``timestamp`` is stored as an ISO-8601 UTC string to keep JSON payloads
    readable and serializable without extra configuration.
    """

    role: MessageRole = Field(..., description="Who authored this message.")
    content: str = Field(
        ..., min_length=1, max_length=32_768, description="Message text content."
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO-8601 UTC timestamp when the message was created.",
    )
    tool_name: str | None = Field(
        default=None,
        description="Name of the tool that produced this message (role=tool only).",
    )

    @field_validator("timestamp")
    @classmethod
    def _validate_iso_timestamp(cls, v: str) -> str:
        """Verify the timestamp can be parsed as a valid ISO-8601 datetime."""
        try:
            datetime.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"Invalid ISO-8601 timestamp: {v!r}") from exc
        return v


class ChatRequest(BaseModel):
    """Request body for ``POST /chat/stream``.

    ``messages`` represents the full conversation history to send to the model.
    ``profile`` and ``inventory`` are injected as context when available so the
    model can personalise responses without re-computing them.
    """

    messages: list[ChatMessage] = Field(
        ..., min_length=1, description="Full conversation history, chronological order."
    )
    session_id: str = Field(..., description="Client-generated string for session tracking.")
    profile: CarbonProfilePartial | None = Field(
        default=None,
        description="Partially or fully-known carbon profile for context injection.",
    )
    inventory: CarbonInventory | None = Field(
        default=None,
        description="Pre-computed carbon inventory to surface in assistant responses.",
    )
    image_base64: str | None = Field(
        default=None,
        max_length=7_000_000,
        description="Optional base64-encoded image (e.g. utility bill) uploaded by the user.",
    )







class ChatStreamEvent(BaseModel):
    """A single SSE frame emitted by the streaming chat endpoint.

    ``type`` is a discriminator consumed by the frontend to route rendering:
    - ``text_delta``: ``data.content`` contains incremental text.
    - ``tool_call``:  ``data.name`` and ``data.args`` describe the invocation.
    - ``error``:      ``data.code`` and ``data.message`` describe the failure.
    - ``done``:       ``data`` is empty; signals end of stream.
    """

    type: StreamEventType = Field(..., description="Event discriminator.")
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Event payload — shape depends on ``type``.",
    )
