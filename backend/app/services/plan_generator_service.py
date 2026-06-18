"""
plan_generator_service.py — generates an execution plan for a specific action.
"""

from __future__ import annotations

import structlog

from app.data.action_catalogue import ACTION_CATALOGUE
from app.models.actions import (
    ExecutionPlan,
    ExecutionPlanResponse,
    ExecutionResource,
    ExecutionStep,
    PlanGenerationRequest,
)
from app.models.carbon import CarbonProfile
from app.services.simulator_service import SimulatorService

logger = structlog.get_logger(__name__)


from typing import Any

# Hardcoded Demo-Ready Execution Steps and Resources
HARDCODED_PLANS: dict[str, Any] = {
    "switch_to_vegan": {
        "timeline_weeks": "1-2 weeks",
        "steps": [
            ExecutionStep(step_number=1, instruction="Audit your pantry and identify easy animal-product swaps."),
            ExecutionStep(step_number=2, instruction="Start with 'Meatless Mondays' or a similar 1-day/week commitment."),
            ExecutionStep(step_number=3, instruction="Gradually replace dairy milk with oat or soy alternatives."),
            ExecutionStep(step_number=4, instruction="Commit to a fully plant-based grocery run for one full week.")
        ],
        "resources": [
            ExecutionResource(title="Veganuary Starter Kit", url="https://veganuary.com/try-vegan/"),
            ExecutionResource(title="Nutrition Facts", url="https://nutritionfacts.org/")
        ]
    },
    "switch_to_vegetarian": {
        "timeline_weeks": "1-2 weeks",
        "steps": [
            ExecutionStep(step_number=1, instruction="Substitute meat with beans or lentils in two standard meals."),
            ExecutionStep(step_number=2, instruction="Learn 3 new vegetarian recipes you genuinely enjoy."),
            ExecutionStep(step_number=3, instruction="Remove meat from your weekly grocery list.")
        ],
        "resources": [
            ExecutionResource(title="Vegetarian Society Guide", url="https://vegsoc.org/")
        ]
    },
    "switch_to_flexitarian": {
        "timeline_weeks": "1 week",
        "steps": [
            ExecutionStep(step_number=1, instruction="Designate weekdays as meat-free days."),
            ExecutionStep(step_number=2, instruction="Limit meat consumption strictly to weekends or special occasions.")
        ],
        "resources": [
            ExecutionResource(title="Flexitarian Guide", url="https://www.healthline.com/nutrition/flexitarian-diet-guide")
        ]
    },
    "eliminate_long_haul": {
        "timeline_weeks": "Immediate",
        "steps": [
            ExecutionStep(step_number=1, instruction="Review your travel plans for the upcoming year."),
            ExecutionStep(step_number=2, instruction="Replace one planned long-haul international vacation with a domestic or regional alternative."),
            ExecutionStep(step_number=3, instruction="Opt for virtual meetings for one major international business trip.")
        ],
        "resources": [
            ExecutionResource(title="Flight Free UK", url="https://flightfree.co.uk/")
        ]
    },
    "eliminate_short_haul": {
        "timeline_weeks": "Immediate",
        "steps": [
            ExecutionStep(step_number=1, instruction="Identify a planned flight that is under 800km."),
            ExecutionStep(step_number=2, instruction="Book a high-speed train or bus alternative instead.")
        ],
        "resources": [
            ExecutionResource(title="Seat61 Train Guide", url="https://www.seat61.com/")
        ]
    },
    "switch_to_ev": {
        "timeline_weeks": "4-8 weeks",
        "steps": [
            ExecutionStep(step_number=1, instruction="Check federal and state EV tax credit eligibility for your income bracket."),
            ExecutionStep(step_number=2, instruction="Test drive 2-3 EV models that fit your budget and range needs."),
            ExecutionStep(step_number=3, instruction="Assess home charging options and get an electrician quote for a Level 2 charger."),
            ExecutionStep(step_number=4, instruction="Trade in your ICE vehicle and complete the EV purchase.")
        ],
        "resources": [
            ExecutionResource(title="Federal EV Tax Credit Info (IRS)", url="https://www.irs.gov/credits-deductions/credits-for-new-clean-vehicles-purchased-in-2023-or-after"),
            ExecutionResource(title="PlugStar EV Shopping Guide", url="https://plugstar.com/")
        ]
    },
    "switch_renewable_tariff": {
        "timeline_weeks": "1 week",
        "steps": [
            ExecutionStep(step_number=1, instruction="Log into your current utility provider's portal."),
            ExecutionStep(step_number=2, instruction="Check if they offer a '100% Green/Renewable' tier and opt in."),
            ExecutionStep(step_number=3, instruction="If unavailable, use a comparison site to switch to a dedicated green energy supplier.")
        ],
        "resources": [
            ExecutionResource(title="EPA Green Power Locator", url="https://www.epa.gov/greenpower/buy-green-power")
        ]
    },
    "switch_to_heat_pump": {
        "timeline_weeks": "6-12 weeks",
        "steps": [
            ExecutionStep(step_number=1, instruction="Schedule a home energy audit to ensure sufficient insulation."),
            ExecutionStep(step_number=2, instruction="Verify eligibility for the $2,000 Federal Tax Credit (25C)."),
            ExecutionStep(step_number=3, instruction="Get quotes from 3 certified HVAC contractors for an air-source heat pump."),
            ExecutionStep(step_number=4, instruction="Proceed with installation and apply for local state rebates.")
        ],
        "resources": [
            ExecutionResource(title="Energy Star Heat Pump Buying Guide", url="https://www.energystar.gov/products/air_source_heat_pumps"),
            ExecutionResource(title="Rewiring America Rebate Calculator", url="https://www.rewiringamerica.org/app/ira-calculator")
        ]
    },
    "halve_clothing_purchases": {
        "timeline_weeks": "Ongoing",
        "steps": [
            ExecutionStep(step_number=1, instruction="Unsubscribe from fast fashion email newsletters."),
            ExecutionStep(step_number=2, instruction="Implement a '30-day rule'—wait 30 days before buying any non-essential clothing."),
            ExecutionStep(step_number=3, instruction="When you must buy, choose second-hand platforms like Vinted, Depop, or ThredUp.")
        ],
        "resources": [
            ExecutionResource(title="Good On You - Ethical Fashion Directory", url="https://goodonyou.eco/")
        ]
    }
}

class PlanGeneratorService:
    def __init__(self, simulator: SimulatorService) -> None:
        self._simulator = simulator

    async def generate_plan(self, request: PlanGenerationRequest) -> ExecutionPlanResponse:
        # 1. Find the Action Template
        action_template = next((a for a in ACTION_CATALOGUE if a.id == request.action_id), None)

        if not action_template:
            raise ValueError(f"Action '{request.action_id}' not found in catalogue.")

        # 2. Simulate to get precise deterministic savings
        from pydantic import TypeAdapter
        profile = TypeAdapter(CarbonProfile).validate_python(request.profile)

        sim_result = await self._simulator.simulate_for_template(
            inventory=request.inventory,
            profile=profile,
            scenario_type=action_template.scenario_type,
            scenario_params=action_template.scenario_params,
        )

        co2e_saved_t = abs(sim_result.delta_co2e)

        # 3. Calculate Financial ROI
        financial_savings_usd = action_template.annual_saving_usd
        upfront_cost_usd = action_template.upfront_cost_usd

        payback_period_years = None
        if upfront_cost_usd > 0 and financial_savings_usd > 0:
            payback_period_years = round(upfront_cost_usd / financial_savings_usd, 1)

        # 4. Fetch the hardcoded implementation steps and resources
        plan_data = HARDCODED_PLANS.get(request.action_id, {
            "timeline_weeks": "Unknown",
            "steps": [ExecutionStep(step_number=1, instruction="Contact a specialist.")],
            "resources": []
        })

        plan = ExecutionPlan(
            action_id=action_template.id,
            title=action_template.title,
            carbon_savings_tco2e=round(co2e_saved_t, 2),
            financial_savings_usd=financial_savings_usd,
            payback_period_years=payback_period_years,
            timeline_weeks=plan_data["timeline_weeks"],
            steps=plan_data["steps"],
            resources=plan_data["resources"]
        )

        logger.info("execution_plan_generated", action_id=request.action_id)

        return ExecutionPlanResponse(plan=plan)
