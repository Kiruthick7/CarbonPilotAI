"""
api/v1/simulate.py
POST /v1/simulate — scenario "What If" simulation endpoint.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, TypeAdapter

from app.dependencies import get_agent, get_simulator
from app.models.carbon import CarbonInventory, CarbonProfile
from app.models.errors import ErrorCode, ErrorResponse
from app.models.simulation import Scenario, SimulateRequest, SimulateResponse
from app.services.agent_service import AgentService
from app.services.simulator_service import SimulatorService

logger = structlog.get_logger(__name__)
router = APIRouter()

class SimulateAIRequest(BaseModel):
    query: str
    inventory: CarbonInventory
    profile: CarbonProfile


@router.post(
    "/simulate",
    response_model=SimulateResponse,
    summary="Simulate a lifestyle scenario",
)
async def simulate_scenario(
    request: SimulateRequest,
    simulator: SimulatorService = Depends(get_simulator),
) -> SimulateResponse:
    """
    Apply a lifestyle change scenario and return the CO₂ delta.
    Examples: switch to vegan diet, reduce long-haul flights by 50%, switch to EV.
    Returns: delta_co2e, delta_percent, co_benefits, optional financial break-even.
    """
    try:
        return await simulator.simulate(request)
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                code=ErrorCode.VAL_INVALID_SCENARIO,
                message=str(e),
            ).model_dump(),
        )
    except Exception as e:
        logger.error("simulate_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                code=ErrorCode.SYS_INTERNAL_ERROR,
                message="Simulation failed.",
            ).model_dump(),
        )

@router.post(
    "/simulate/ai",
    response_model=SimulateResponse,
    summary="Simulate a scenario using an AI natural language prompt",
)
async def simulate_ai_scenario(
    request: SimulateAIRequest,
    simulator: SimulatorService = Depends(get_simulator),
    agent: AgentService = Depends(get_agent),
) -> SimulateResponse:
    """
    Parses a natural language query into simulation scenarios and evaluates them.
    """
    try:
        scenario_dicts = await agent.parse_simulate_query(request.query)
        if not scenario_dicts:
            raise ValueError("Could not understand any actionable scenarios from your query. Try being more specific, e.g., 'Switch to an EV'.")

        ta: TypeAdapter[Scenario] = TypeAdapter(Scenario)
        scenarios = [ta.validate_python(sd) for sd in scenario_dicts]

        sim_request = SimulateRequest(
            inventory=request.inventory,
            profile=request.profile,
            scenarios=scenarios
        )
        return await simulator.simulate(sim_request)
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                code=ErrorCode.VAL_INVALID_SCENARIO,
                message=str(e),
            ).model_dump(),
        )
    except Exception as e:
        logger.error("simulate_ai_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                code=ErrorCode.SYS_INTERNAL_ERROR,
                message="AI Simulation failed.",
            ).model_dump(),
        )
