"""
agent_service.py — Python 3.9 compatible (no match/case).
Groq agent orchestration with tool calling and graceful degradation.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

import structlog

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    AsyncGroq = None  # type: ignore[assignment, misc]

from app.agent.prompts import SYSTEM_PROMPT, build_user_message
from app.agent.tools import TOOL_DEFINITIONS
from app.config import get_settings
from app.models.carbon import CarbonProfile
from app.models.chat import ChatRequest
from app.services.calculator_service import CalculatorService
from app.services.ranker_service import RankerService
from app.services.simulator_service import SimulatorService

logger = structlog.get_logger(__name__)

FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]


class AgentService:
    """
    Orchestrates the Groq agent with tool calling.
    Tool implementations live here; schemas in tools.py.
    """

    def __init__(
        self,
        calculator: CalculatorService,
        simulator: SimulatorService,
        ranker: RankerService,
    ) -> None:
        self._calculator = calculator
        self._simulator = simulator
        self._ranker = ranker
        self._session_constraints: dict[str, Any] = {}
        self._client: Any = None

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

    async def _create_completion_with_fallback(self, **kwargs):
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

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[dict[str, Any], None]:
        """Main streaming chat loop. Yields SSE-compatible event dicts."""
        session_id = request.session_id
        constraints = self._session_constraints.get(session_id, {})

        if not self._ai_ready:
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

            parsed_bill = await self._tool_parse_bill({"image_base64": request.image_base64})
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
            response_stream = await self._create_completion_with_fallback(
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
                    except Exception:
                        fn_args = {}

                    tool_result = await self._dispatch_tool(fn_name, fn_args, request, constraints)
                    yield {"type": "tool_call", "data": {"tool": fn_name, "result": tool_result}}

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": fn_name,
                        "content": json.dumps(tool_result, default=str)
                    })


                follow_up_stream = await self._create_completion_with_fallback(
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



    async def _dispatch_tool(
        self, name: str, args: dict[str, Any], request: ChatRequest, constraints: dict[str, Any]
    ) -> Any:
        if name == "calculate_footprint":
            return await self._tool_calculate(args, request)
        elif name == "simulate_scenario":
            return await self._tool_simulate(args, request)
        elif name == "rank_actions":
            return await self._tool_rank(args, request, constraints)
        elif name == "record_constraint":
            return self._tool_record_constraint(args, request.session_id, constraints)
        elif name == "parse_utility_bill":
            return await self._tool_parse_bill(args)
        elif name == "suggest_quick_replies":
            return {"options": args.get("options", [])}
        else:
            logger.warning("unknown_tool_call", tool=name)
            return {"error": f"Unknown tool: {name}"}

    async def _tool_calculate(self, args: dict[str, Any], request: ChatRequest) -> dict:
        try:
            profile_data = args.get("profile", {})
            if request.profile:
                base = request.profile.model_dump(exclude_none=True)
                for k, v in profile_data.items():
                    if isinstance(v, dict) and isinstance(base.get(k), dict):
                        base[k].update(v)
                    elif v is not None:

                        if k == "country_code" and base.get("country_code"):
                            continue
                        base[k] = v
                profile_data = base

            if "transport" not in profile_data:
                profile_data["transport"] = {}

            if "diet" not in profile_data:
                profile_data["diet"] = {"diet_type": "omnivore"}
            else:
                diet_type = profile_data["diet"].pop("type", None) or profile_data["diet"].get("diet_type", "omnivore")
                if diet_type not in ["vegan", "vegetarian", "flexitarian", "omnivore", "meat_heavy"]:
                    diet_type = "omnivore"
                profile_data["diet"]["diet_type"] = diet_type

            if "transport" in profile_data:
                transport = profile_data["transport"]
                if "flights" in transport and isinstance(transport["flights"], (int, float, str)):

                    try:
                        val = int(transport["flights"])
                        transport["flights"] = {"long_haul_flights": val}
                    except ValueError:
                        transport["flights"] = {}

            if "home" not in profile_data:
                profile_data["home"] = {"home_size": "medium", "heating_type": "gas"}
            else:
                if "home_size" not in profile_data["home"]:
                    profile_data["home"]["home_size"] = "medium"
                if "heating_type" not in profile_data["home"]:
                    profile_data["home"]["heating_type"] = "gas"

            profile = CarbonProfile.model_validate(profile_data)
            result = await self._calculator.calculate(profile)
            return {
                "inventory": result["inventory"].model_dump(),
                "version": result["calculation_version"],
                "profile": profile.model_dump()
            }
        except Exception as e:
            logger.error("tool_calculate_error", error=str(e))
            return {"error": "An internal error occurred while processing this action."}

    async def _tool_simulate(self, args: dict[str, Any], request: ChatRequest) -> dict:
        try:
            if not request.inventory:
                return {"error": "No inventory. Run calculate_footprint first."}
            from pydantic import TypeAdapter

            from app.models.simulation import Scenario, SimulateRequest
            scenario = TypeAdapter(Scenario).validate_python({"type": args["scenario_type"], **args["scenario_params"]})
            profile_data = request.profile.model_dump(exclude_none=True) if request.profile else {}
            profile = CarbonProfile.model_validate(profile_data)
            sim_request = SimulateRequest(inventory=request.inventory, profile=profile, scenario=scenario)
            result = await self._simulator.simulate(sim_request)
            return result.model_dump()
        except Exception as e:
            logger.error("tool_simulate_error", error=str(e))
            return {"error": "An internal error occurred while processing this action."}

    async def _tool_rank(self, args: dict[str, Any], request: ChatRequest, constraints: dict[str, Any]) -> dict:
        try:
            if not request.inventory:
                return {"error": "No inventory. Run calculate_footprint first."}
            from app.models.actions import RankActionsRequest, UserConstraints
            merged = {**constraints, **(args.get("constraints") or {})}
            rank_request = RankActionsRequest(inventory=request.inventory, constraints=UserConstraints.model_validate(merged))
            profile_data = request.profile.model_dump(exclude_none=True) if request.profile else {}
            profile = CarbonProfile.model_validate(profile_data)
            result = await self._ranker.rank(rank_request, profile)
            return result.model_dump()
        except Exception as e:
            logger.error("tool_rank_error", error=str(e))
            return {"error": "An internal error occurred while processing this action."}

    def _tool_record_constraint(self, args: dict[str, Any], session_id: str, constraints: dict[str, Any]) -> dict:
        constraint_type = args.get("constraint_type", "")
        constraint_map = {
            "rents_home": {"lifestyle_flags": {"rents_home": True}},
            "rural_location": {"lifestyle_flags": {"rural_location": True}},
            "no_budget": {"max_upfront_cost_usd": 0},
            "work_travel": {"exclude_categories": ["transport"]},
            "medical_diet": {"exclude_categories": ["diet"]},
        }
        update = constraint_map.get(constraint_type, {})
        for k, v in update.items():
            if isinstance(v, dict) and k in constraints:
                constraints[k].update(v)
            else:
                constraints[k] = v
        self._session_constraints[session_id] = constraints
        return {"recorded": constraint_type}

    async def _tool_parse_bill(self, args: dict[str, Any]) -> dict:
        try:
            image_b64 = args.get("image_base64", "")
            if not image_b64 or not self._client:
                return {"error": "No image provided or AI unavailable"}

            if "," in image_b64:
                image_b64 = image_b64.split(",", 1)[1]

            image_url = f"data:image/jpeg;base64,{image_b64}"

            prompt = (
                "You are an expert OCR AI. Extract data from this utility bill image. "
                "Look for terms like 'Units', 'kWh', 'Total Unit', or 'Consumption'. "
                "If you see 'Total Unit', use that number for total_kwh. "
                "Extract: "
                "1. total_kwh (number or null): The total energy consumed. Example: if Total Unit is 3535, use 3535. "
                "2. period_months (number): The billing period length in months (default 1). Calculate from 'Period' dates if available. "
                "3. tariff_name (string or null). "
                "4. is_renewable (boolean or null). "
                "Return ONLY a raw JSON object with these exactly named keys. Do not include markdown formatting or any other text."
            )

            response = await self._client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                }
                            },
                        ],
                    }
                ],
                temperature=0.0,
            )

            raw_content = response.choices[0].message.content or "{}"

            raw_content = raw_content.replace("```json", "").replace("```", "").strip()
            logger.info(f"Vision model raw content: {raw_content}")
            raw_data = json.loads(raw_content)


            from pydantic import BaseModel, Field
            class ParsedBill(BaseModel):
                total_kwh: float | None = Field(default=None, ge=0, le=100000, description="Total kWh used")
                period_months: int = Field(default=1, ge=1, le=12, description="Billing period in months")
                tariff_name: str | None = Field(default=None, description="Name of the tariff or plan")
                is_renewable: bool | None = Field(default=None, description="Whether the plan is 100% renewable")

            validated = ParsedBill.model_validate(raw_data)
            return validated.model_dump()

        except Exception as e:
            logger.error("bill_parse_error", error=str(e))
            return {"error": "Could not read a valid utility bill from that image. Please upload a clearer photo or enter your usage manually."}

    async def parse_simulate_query(self, query: str) -> list[dict[str, Any]]:
        """Parses a natural language query into a list of Scenario parameter dicts."""
        if not self._ai_ready:
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
        response = await self._create_completion_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        try:
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            return data.get("scenarios", [])
        except Exception as e:
            logger.error("parse_simulate_query_error", error=str(e))
            return []
