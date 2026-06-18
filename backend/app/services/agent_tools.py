import json
from typing import Any

import structlog

from app.models.carbon import CarbonProfile
from app.models.chat import ChatRequest
from app.services.calculator_service import CalculatorService
from app.services.llm_client import LLMClient
from app.services.ranker_service import RankerService
from app.services.simulator_service import SimulatorService

logger = structlog.get_logger(__name__)

class AgentTools:
    def __init__(self, calculator: CalculatorService, simulator: SimulatorService, ranker: RankerService, llm_client: LLMClient) -> None:
        self._calculator = calculator
        self._simulator = simulator
        self._ranker = ranker
        self._llm_client = llm_client

    async def dispatch_tool(self, name: str, args: dict[str, Any], request: ChatRequest, constraints: dict[str, Any], session_constraints: dict[str, Any], session_id: str) -> Any:
        if name == "calculate_footprint":
            return await self.tool_calculate(args, request)
        elif name == "simulate_scenario":
            return await self.tool_simulate(args, request)
        elif name == "rank_actions":
            return await self.tool_rank(args, request, constraints)
        elif name == "record_constraint":
            return self.tool_record_constraint(args, session_id, constraints, session_constraints)
        elif name == "parse_utility_bill":
            return await self.tool_parse_bill(args)
        elif name == "suggest_quick_replies":
            return {"options": args.get("options", [])}
        else:
            logger.warning("unknown_tool_call", tool=name)
            return {"error": f"Unknown tool: {name}"}

    async def tool_calculate(self, args: dict[str, Any], request: ChatRequest) -> dict[str, Any]:
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

    async def tool_simulate(self, args: dict[str, Any], request: ChatRequest) -> dict[str, Any]:
        try:
            if not request.inventory:
                return {"error": "No inventory. Run calculate_footprint first."}
            from pydantic import TypeAdapter

            from app.models.simulation import Scenario, SimulateRequest
            scenario: Scenario = TypeAdapter(Scenario).validate_python({"type": args["scenario_type"], **args["scenario_params"]})
            profile_data = request.profile.model_dump(exclude_none=True) if request.profile else {}
            profile = CarbonProfile.model_validate(profile_data)
            sim_request = SimulateRequest(inventory=request.inventory, profile=profile, scenario=scenario)
            result = await self._simulator.simulate(sim_request)
            return result.model_dump()
        except Exception as e:
            logger.error("tool_simulate_error", error=str(e))
            return {"error": "An internal error occurred while processing this action."}

    async def tool_rank(self, args: dict[str, Any], request: ChatRequest, constraints: dict[str, Any]) -> dict[str, Any]:
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

    def tool_record_constraint(self, args: dict[str, Any], session_id: str, constraints: dict[str, Any], session_constraints: dict[str, Any]) -> dict[str, Any]:
        constraint_type = args.get("constraint_type", "")
        constraint_map: dict[str, dict[str, Any]] = {
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
        session_constraints[session_id] = constraints
        return {"recorded": constraint_type}

    async def tool_parse_bill(self, args: dict[str, Any]) -> dict[str, Any]:
        try:
            image_b64 = args.get("image_base64", "")
            if not image_b64 or not self._llm_client.ai_ready:
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

            response = await self._llm_client.client.chat.completions.create(
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
