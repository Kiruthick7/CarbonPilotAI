"""
ranker_service.py — aligned to existing CarbonInventory model.
Generates a personalised, ranked list of up to 5 climate actions.
"""

from __future__ import annotations

import asyncio

import structlog

from app.engines.ranking_engine import RankingEngine
from app.models.actions import RankActionsRequest, RankActionsResponse, UserConstraints
from app.models.carbon import CarbonProfile
from app.services.simulator_service import SimulatorService

logger = structlog.get_logger(__name__)

MAX_ACTIONS = 5


class RankerService:
    """
    Coordinates action ranking:
      1. Filter catalogue to relevant + feasible actions
      2. Simulate all candidates in parallel (asyncio.gather)
      3. Score each via RankingEngine
      4. Return top MAX_ACTIONS sorted by composite score
    """

    def __init__(self, simulator: SimulatorService) -> None:
        self._engine = RankingEngine()
        self._simulator = simulator

    async def rank(
        self,
        request: RankActionsRequest,
        profile: CarbonProfile,
    ) -> RankActionsResponse:
        constraints = request.constraints or UserConstraints()
        candidates = self._engine.generate_candidates(request.inventory, constraints, profile)

        logger.info("ranking_actions", candidate_count=len(candidates))

        simulations = await asyncio.gather(
            *[
                self._simulator.simulate_for_template(
                    inventory=request.inventory,
                    profile=profile,
                    scenario_type=candidate.scenario_type,
                    scenario_params=candidate.scenario_params,
                )
                for candidate in candidates
            ],
            return_exceptions=True,
        )

        ranked_actions = []

        total_kg = request.inventory.total_tco2e * 1000

        for template, sim_result in zip(candidates, simulations, strict=False):
            if isinstance(sim_result, Exception):
                logger.warning("action_simulation_failed", action_id=template.id, error=str(sim_result))
                continue

            co2e_saved_t = abs(sim_result.delta_co2e)
            ranked_action = self._engine.build_ranked_action(
                template=template,
                co2e_saved_t=co2e_saved_t,
                co_benefits=sim_result.co_benefits,
                total_footprint_kg=total_kg,
                constraints=constraints,
            )
            ranked_actions.append(ranked_action)

        def _sort_actions():
            ranked_actions.sort(
                key=lambda a: (a.is_feasible, a.composite_score),
                reverse=True,
            )
            return ranked_actions[:MAX_ACTIONS]

        top = await asyncio.to_thread(_sort_actions)
        total_achievable = sum(a.co2e_saved_per_year for a in top if a.is_feasible)

        logger.info("ranking_complete", top_action=top[0].id if top else None)

        return RankActionsResponse(
            actions=top,
            total_achievable_reduction=round(total_achievable, 3),
        )
