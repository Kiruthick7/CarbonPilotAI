"""
api/v1/chat.py
POST /v1/chat — streaming AI conversation endpoint.
Returns Server-Sent Events (SSE).
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import get_agent
from app.models.chat import ChatRequest
from app.services.agent_service import AgentService

logger = structlog.get_logger(__name__)
router = APIRouter()


async def _event_stream(
    request: ChatRequest, agent: AgentService
) -> AsyncGenerator[str, None]:
    """Convert agent generator output to SSE wire format."""
    try:
        async for chunk in agent.stream_chat(request):
            data = json.dumps(chunk, default=str)
            yield f"data: {data}\n\n"
    except Exception as e:
        logger.error("chat_stream_error", error=str(e), exc_info=True)
        error_chunk = {"type": "error", "data": {"message": "An unexpected error occurred during the stream.", "details": str(e)}}
        yield f"data: {json.dumps(error_chunk, default=str)}\n\n"


@router.post(
    "/chat",
    summary="Streaming AI chat",
    response_description="Server-Sent Events stream of text deltas and tool call results",
)
async def chat(
    request: ChatRequest,
    agent: AgentService = Depends(get_agent),
) -> StreamingResponse:
    """
    Streaming AI sustainability coaching conversation.
    Returns an SSE stream with event types:
    - text_delta: AI text chunk
    - tool_call: structured tool result (calculate/simulate/rank)
    - error: degraded mode notification
    - done: stream complete
    """
    logger.info("chat_request", session_id=request.session_id, message_count=len(request.messages))
    return StreamingResponse(
        _event_stream(request, agent),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
