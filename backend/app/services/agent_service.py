"""
agent_service.py — Python 3.9 compatible (no match/case).
Groq agent orchestration with tool calling and graceful degradation.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any, cast

import structlog

from app.agent.prompts import SYSTEM_PROMPT, build_user_message
from app.agent.tools import TOOL_DEFINITIONS
from app.models.chat import ChatRequest
from app.services.agent_tools import AgentTools
from app.services.calculator_service import CalculatorService
from app.services.llm_client import LLMClient
from app.services.ranker_service import RankerService
from app.services.simulator_service import SimulatorService

logger = structlog.get_logger(__name__)

class AgentService:
    """
    Orchestrates the Groq agent with tool calling.
    """

    def __init__(
        self,
        calculator: CalculatorService,
        simulator: SimulatorService,
        ranker: RankerService,
    ) -> None:
        self._llm_client = LLMClient()
        self._agent_tools = AgentTools(calculator, simulator, ranker, self._llm_client)
        self._session_constraints: dict[str, Any] = {}

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[dict[str, Any], None]:
        """Main streaming chat loop. Yields SSE-compatible event dicts."""
        session_id = request.session_id
        constraints = self._session_constraints.get(session_id, {})

        if not self._llm_client.ai_ready:
            yield {
                "type": "error",
                "data": {
                    "code": "AI_UNAVAILABLE",
                    "fallback_mode": True,
                    "message": "AI coaching is temporarily unavailable. Your calculator still works.",
                },
            }
            return

        history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in request.messages[:-1]
        ]

        current_message_text = request.messages[-1].content

        if request.image_base64:
            parsed_bill = await self._agent_tools.tool_parse_bill({"image_base64": request.image_base64})
            yield {"type": "tool_call", "data": {"tool": "parse_utility_bill", "result": parsed_bill}}

            history.append({
                "role": "system",
                "content": f"I have parsed the uploaded utility bill. The extracted data is: {json.dumps(parsed_bill)}. Acknowledge the upload, summarize the findings, and ask if I should update their profile."
            })

        current_message = build_user_message(current_message_text)

        context_prefix = ""
        if request.profile:
            context_prefix = f"[Profile: {request.profile.model_dump_json(exclude_none=True)}]\n\n"

        messages: list[Any] = [{"role": "system", "content": SYSTEM_PROMPT}, *history, {"role": "user", "content": context_prefix + current_message}]

        try:
            response_stream = await self._llm_client.create_completion_with_fallback(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0.4,
                stream=True,
            )

            tool_calls: dict[int, Any] = {}
            content_buffer = ""

            async for chunk in response_stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    content_buffer += delta.content
                    yield {"type": "text_delta", "data": {"delta": delta.content}}
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        if tc.index not in tool_calls:
                            tool_calls[tc.index] = {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.function.name, "arguments": ""}
                            }
                        if tc.function.arguments:
                            tool_calls[tc.index]["function"]["arguments"] += tc.function.arguments


            import re
            matches = re.finditer(r"<function=([^>]+)>(.*?)</function>", content_buffer, re.DOTALL)
            for m in matches:
                fn_name = m.group(1).strip()
                fn_args_str = m.group(2).strip()
                idx = len(tool_calls)
                tool_calls[idx] = {
                    "id": f"call_{fn_name}_{idx}",
                    "type": "function",
                    "function": {"name": fn_name, "arguments": fn_args_str}
                }


            if tool_calls:
                assistant_message = {"role": "assistant", "content": None, "tool_calls": list(tool_calls.values())}
                messages.append(assistant_message)

                for tc in tool_calls.values():
                    fn_name = tc["function"]["name"]
                    try:
                        fn_args = json.loads(str(tc["function"]["arguments"]))
                    except json.JSONDecodeError as e:
                        logger.warning("agent_tool_args_parse_failed", error=str(e), tool=fn_name)
                        fn_args = {}

                    tool_result = await self._agent_tools.dispatch_tool(fn_name, fn_args, request, constraints, self._session_constraints, session_id)
                    yield {"type": "tool_call", "data": {"tool": fn_name, "result": tool_result}}

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": fn_name,
                        "content": json.dumps(tool_result, default=str)
                    })


                follow_up_stream = await self._llm_client.create_completion_with_fallback(
                    messages=messages,
                    temperature=0.4,
                    stream=True,
                )
                async for chunk in follow_up_stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield {"type": "text_delta", "data": {"delta": delta.content}}

            yield {"type": "done", "data": {"session_id": session_id}}

        except Exception as exc:
            logger.error("agent_stream_error", error=str(exc), session_id=session_id)
            yield {
                "type": "error",
                "data": {
                    "code": "AI_UNAVAILABLE",
                    "fallback_mode": True,
                    "message": "AI coaching is temporarily unavailable. Your calculator still works.",
                },
            }



    async def parse_simulate_query(self, query: str) -> list[dict[str, Any]]:
        """Parses a natural language query into a list of Scenario parameter dicts."""
        if not self._llm_client.ai_ready:
            raise RuntimeError("AI unavailable.")

        schema = {
            "type": "object",
            "properties": {
                "scenarios": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["switch_diet", "switch_car", "reduce_flights", "switch_heating", "add_renewable", "reduce_consumption", "extend_devices", "reduce_streaming"]},
                            "new_diet": {"type": "string", "enum": ["vegan", "vegetarian", "flexitarian", "omnivore", "meat_heavy"]},
                            "new_car_type": {"type": "string", "enum": ["petrol", "diesel", "hybrid", "electric", "none"]},
                            "reduce_short_haul_by": {"type": "integer"},
                            "reduce_long_haul_by": {"type": "integer"},
                            "new_heating_type": {"type": "string", "enum": ["gas", "oil", "electric", "heat_pump", "biomass"]},
                            "switch_to_renewable_tariff": {"type": "boolean"},
                            "add_solar_panels": {"type": "boolean"},
                            "reduce_clothing_by": {"type": "integer"},
                            "reduce_electronics_by": {"type": "integer"},
                            "reduce_deliveries_by": {"type": "number"},
                            "new_device_frequency": {"type": "string", "enum": ["frequent", "average", "rare"]},
                            "new_streaming_usage": {"type": "string", "enum": ["light", "moderate", "heavy"]}
                        },
                        "required": ["type"]
                    }
                }
            },
            "required": ["scenarios"]
        }

        prompt = f"""
You are an expert at mapping user intents into structured carbon simulation scenarios.
Map this query: "{query}"

Return a JSON object matching this schema:
{json.dumps(schema)}

Only include the scenario types and parameters explicitly requested.
"""
        response = await self._llm_client.create_completion_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        try:
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            return cast(list[dict[str, Any]], data.get("scenarios", []))
        except Exception as e:
            logger.error("parse_simulate_query_error", error=str(e))
            return []
