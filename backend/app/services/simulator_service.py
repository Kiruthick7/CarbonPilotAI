from __future__ import annotations

from typing import Any

"""
simulator_service.py — aligned to existing models.
"""


import structlog

from app.engines.simulation_engine import SimulationEngine
from app.models.carbon import CarbonInventory, CarbonProfile
from app.models.simulation import Scenario, SimulateRequest, SimulateResponse
from app.services.calculator_service import CalculatorService

logger = structlog.get_logger(__name__)


class SimulatorService:
    """
    Applies a scenario to a profile, recalculates, and returns the delta.
    """

    def __init__(self, calculator: CalculatorService) -> None:
        self._engine = SimulationEngine()
        self._calculator = calculator

    async def simulate(self, request: SimulateRequest) -> SimulateResponse:
        all_scenarios = request.scenarios or []
        if request.scenario and request.scenario not in all_scenarios:
            all_scenarios.append(request.scenario)

        logger.info(
            "simulating_scenarios",
            num_scenarios=len(all_scenarios),
            original_total=request.inventory.total_tco2e,
        )

        modified_profile = request.profile
        for sc in all_scenarios:
            modified_profile = self._engine.apply_scenario(
                profile=modified_profile,
                scenario=sc,
            )

        new_result = await self._calculator.calculate(modified_profile)
        new_inventory: CarbonInventory = new_result["inventory"]

        response = self._engine.compute_delta(
            original=request.inventory,
            new=new_inventory,
            scenario=request.scenario,
            scenarios=request.scenarios,
        )

        logger.info(
            "simulation_complete",
            delta_co2e=response.delta_co2e,
            delta_percent=response.delta_percent,
        )
        return response

    async def simulate_for_template(
        self,
        inventory: CarbonInventory,
        profile: CarbonProfile,
        scenario_type: str,
        scenario_params: dict[str, Any],
    ) -> SimulateResponse:
        """Convenience method for the ranker — builds a SimulateRequest from parts."""
        from pydantic import TypeAdapter

        scenario: Scenario = TypeAdapter(Scenario).validate_python(
            {"type": scenario_type, **scenario_params}
        )
        return await self.simulate(
            SimulateRequest(
                inventory=inventory,
                profile=profile,
                scenario=scenario,
            )
        )
