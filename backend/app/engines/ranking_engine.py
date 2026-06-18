"""
ranking_engine.py — Python 3.9 compatible. No match/case.
Impact-vs-effort ranking algorithm for personalised action recommendations.

Algorithm:
  composite_score = 0.70 × impact_norm + 0.20 × effort_norm + 0.05 × speed_norm + 0.05 × coben_bonus
  impact_norm uses sqrt curve to prevent one action dominating.
  Feasibility is a hard filter.
"""
from __future__ import annotations

import math
from collections.abc import Callable

from app.models.actions import ActionCategory, RankedAction, UserConstraints
from app.models.carbon import CarbonInventory, CarbonProfile
from app.models.simulation import CoBenefit


class ActionTemplate:
    """Static definition of a possible action."""

    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        category: ActionCategory,
        scenario_type: str,
        scenario_params: dict,
        base_effort_score: int,
        time_to_impact_days: int,
        upfront_cost_usd: float = 0.0,
        annual_saving_usd: float = 0.0,
        is_relevant: Callable[[CarbonInventory], bool] | None = None,
        is_allowed: Callable[[UserConstraints], bool] | None = None,
    ) -> None:
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.scenario_type = scenario_type
        self.scenario_params = scenario_params
        self.base_effort_score = base_effort_score
        self.time_to_impact_days = time_to_impact_days
        self.upfront_cost_usd = upfront_cost_usd
        self.annual_saving_usd = annual_saving_usd
        self.is_relevant: Callable[[CarbonInventory], bool] = is_relevant or (lambda _: True)
        self.is_allowed: Callable[[UserConstraints], bool] = is_allowed or (lambda _: True)


def _diet_transport_kg(inv: CarbonInventory, category: str) -> float:
    for bd in inv.breakdowns:
        if bd.category == category:
            return bd.total_kgco2e
    return 0.0


def _sub_kg(inv: CarbonInventory, category: str, label: str) -> float:
    for bd in inv.breakdowns:
        if bd.category == category:
            for sub in bd.subcategories:
                if sub.label == label:
                    return sub.kgco2e
    return 0.0


ACTION_CATALOGUE: list[ActionTemplate] = [
    ActionTemplate(
        id="switch_to_vegan",
        title="Switch to a fully plant-based diet",
        description="Eliminating all animal products cuts your diet footprint by up to 75%.",
        category=ActionCategory.DIET,
        scenario_type="switch_diet",
        scenario_params={"new_diet": "vegan"},
        base_effort_score=3,
        time_to_impact_days=1,
        annual_saving_usd=1500.0,
    ),
    ActionTemplate(
        id="switch_to_vegetarian",
        title="Go vegetarian",
        description="Removing meat (keeping eggs and dairy) cuts diet emissions by ~50%.",
        category=ActionCategory.DIET,
        scenario_type="switch_diet",
        scenario_params={"new_diet": "vegetarian"},
        base_effort_score=2,
        time_to_impact_days=1,
        annual_saving_usd=900.0,
        is_relevant=lambda inv: _diet_transport_kg(inv, "diet") > 1500,
    ),
    ActionTemplate(
        id="switch_to_flexitarian",
        title="Reduce meat to 2–3 meals per week",
        description="Cutting meat frequency is the easiest high-impact dietary change.",
        category=ActionCategory.DIET,
        scenario_type="switch_diet",
        scenario_params={"new_diet": "flexitarian"},
        base_effort_score=1,
        time_to_impact_days=1,
        annual_saving_usd=500.0,
        is_relevant=lambda inv: _diet_transport_kg(inv, "diet") > 2500,
    ),
    ActionTemplate(
        id="eliminate_long_haul",
        title="Skip one long-haul flight this year",
        description="One return transatlantic flight adds ~3.1 tCO₂e — more than a year of car driving for most.",
        category=ActionCategory.TRANSPORT,
        scenario_type="reduce_flights",
        scenario_params={"reduce_long_haul_by": 1},
        base_effort_score=2,
        time_to_impact_days=0,
        annual_saving_usd=1200.0,
        is_relevant=lambda inv: _sub_kg(inv, "transport", "Long-haul flights") > 300,
    ),
    ActionTemplate(
        id="eliminate_short_haul",
        title="Replace short-haul flights with train",
        description="Trains emit 5–10× less than equivalent flights under 800km.",
        category=ActionCategory.TRANSPORT,
        scenario_type="reduce_flights",
        scenario_params={"reduce_short_haul_by": 1},
        base_effort_score=2,
        time_to_impact_days=0,
        annual_saving_usd=400.0,
        is_relevant=lambda inv: _sub_kg(inv, "transport", "Short-haul flights") > 100,
    ),
    ActionTemplate(
        id="switch_to_ev",
        title="Switch to an electric vehicle",
        description="EVs emit 50–80% less per km than petrol cars on today's grid.",
        category=ActionCategory.TRANSPORT,
        scenario_type="switch_car",
        scenario_params={"new_car_type": "electric"},
        base_effort_score=5,
        time_to_impact_days=90,
        upfront_cost_usd=8000.0,
        annual_saving_usd=1500.0,
        is_relevant=lambda inv: _sub_kg(inv, "transport", "Car") > 500,
    ),
    ActionTemplate(
        id="switch_renewable_tariff",
        title="Switch to a 100% renewable electricity tariff",
        description="Takes 10 minutes online and immediately cuts your electricity footprint by 95%.",
        category=ActionCategory.HOME,
        scenario_type="add_renewable",
        scenario_params={"switch_to_renewable_tariff": True},
        base_effort_score=1,
        time_to_impact_days=7,
        upfront_cost_usd=0.0,
        annual_saving_usd=0.0,
    ),
    ActionTemplate(
        id="switch_to_heat_pump",
        title="Replace gas boiler with a heat pump",
        description="Heat pumps deliver 3× more heat energy than the electricity they consume.",
        category=ActionCategory.HOME,
        scenario_type="switch_heating",
        scenario_params={"new_heating_type": "heat_pump"},
        base_effort_score=5,
        time_to_impact_days=60,
        upfront_cost_usd=12000.0,
        annual_saving_usd=700.0,
        is_allowed=lambda c: not c.lifestyle_flags.get("rents_home", False),
        is_relevant=lambda inv: _diet_transport_kg(inv, "home") > 1000,
    ),
    ActionTemplate(
        id="halve_clothing_purchases",
        title="Buy half as many new clothing items",
        description="Fashion produces ~10% of global CO₂. Buying less is the only sustainable solution.",
        category=ActionCategory.CONSUMPTION,
        scenario_type="reduce_consumption",
        scenario_params={"reduce_clothing_by": 10},
        base_effort_score=2,
        time_to_impact_days=30,
        annual_saving_usd=800.0,
    ),
    ActionTemplate(
        id="extend_device_lifespan",
        title="Keep your phone and laptop for an extra year",
        description="Extending the lifecycle of your devices significantly reduces your embodied carbon footprint.",
        category=ActionCategory.DIGITAL,
        scenario_type="extend_devices",
        scenario_params={"new_device_frequency": "rare"},
        base_effort_score=2,
        time_to_impact_days=365,
        annual_saving_usd=300.0,
        is_relevant=lambda inv: _sub_kg(inv, "digital", "Embodied (Hardware)") > 50,
    ),
    ActionTemplate(
        id="reduce_streaming_quality",
        title="Switch default streaming quality to 1080p",
        description="Dropping from 4K to 1080p reduces data center and transmission emissions by up to 75%.",
        category=ActionCategory.DIGITAL,
        scenario_type="reduce_streaming",
        scenario_params={"new_streaming_usage": "light"},
        base_effort_score=1,
        time_to_impact_days=1,
        annual_saving_usd=0.0,
        is_relevant=lambda inv: _sub_kg(inv, "digital", "Operational (Streaming & AI)") > 20,
    ),
]


def normalise_impact(co2e_saved_kg: float, total_footprint_kg: float) -> float:
    if total_footprint_kg <= 0:
        return 0.0
    raw = co2e_saved_kg / total_footprint_kg
    return round(min(math.sqrt(max(raw, 0.0)), 1.0), 4)


def normalise_effort(effort_score: int) -> float:
    return round((6 - effort_score) / 5.0, 2)


def normalise_speed(time_to_impact_days: int) -> float:
    return round(max(0.0, 1.0 - (time_to_impact_days / 365.0)), 2)


class RankingEngine:
    """Scores and ranks action templates against a user's inventory."""

    WEIGHTS: dict[str, float] = {"impact": 0.70, "effort": 0.20, "speed": 0.05, "coben": 0.05}

    def generate_candidates(
        self,
        inventory: CarbonInventory,
        constraints: UserConstraints,
        profile: CarbonProfile,
    ) -> list[ActionTemplate]:
        candidates = []
        for a in ACTION_CATALOGUE:
            if not a.is_relevant(inventory): continue
            if not a.is_allowed(constraints): continue
            if a.category.value in constraints.exclude_categories: continue


            if a.category.value == "diet" and profile.diet is None: continue
            if a.category.value == "transport" and profile.transport is None: continue
            if a.category.value == "consumption" and profile.consumption is None: continue
            if a.category.value == "home" and profile.home is None: continue
            if a.category.value == "digital" and profile.digital is None: continue


            stype = a.scenario_type
            if stype == "switch_diet" and profile.diet and profile.diet.diet_type.value == a.scenario_params.get("new_diet"): continue
            if stype == "switch_car" and profile.transport and profile.transport.car and profile.transport.car.car_type.value == a.scenario_params.get("new_car_type"): continue
            if stype == "switch_heating" and profile.home and profile.home.heating_type.value == a.scenario_params.get("new_heating_type"): continue
            if stype == "add_renewable" and profile.home and profile.home.renewable_tariff and a.scenario_params.get("switch_to_renewable_tariff"): continue
            if stype == "extend_devices" and profile.digital and profile.digital.device_upgrade_frequency.value == a.scenario_params.get("new_device_frequency"): continue
            if stype == "reduce_streaming" and profile.digital and profile.digital.streaming_gaming_usage.value == a.scenario_params.get("new_streaming_usage"): continue

            candidates.append(a)

        return candidates

    def score(
        self,
        template: ActionTemplate,
        co2e_saved_kg: float,
        total_footprint_kg: float,
        co_benefits: list[CoBenefit],
    ) -> float:


        cost_factor = max(1.0, template.upfront_cost_usd / 1000.0)
        impact = normalise_impact(co2e_saved_kg, total_footprint_kg)


        roi_score = (impact / cost_factor) * (1.0 / template.base_effort_score)


        speed  = self.WEIGHTS["speed"]  * normalise_speed(template.time_to_impact_days)
        coben  = self.WEIGHTS["coben"]  * min(len(co_benefits) * 0.05, 0.05)

        return round(roi_score + speed + coben, 4)

    def build_ranked_action(
        self,
        template: ActionTemplate,
        co2e_saved_t: float,
        co_benefits: list[CoBenefit],
        total_footprint_kg: float,
        constraints: UserConstraints,
    ) -> RankedAction:
        feasible = template.is_allowed(constraints)
        composite = self.score(template, co2e_saved_t * 1000, total_footprint_kg, co_benefits)
        impact_score = min(5, max(1, round(normalise_impact(co2e_saved_t * 1000, total_footprint_kg) * 5)))

        if template.category.value == "home":
             why = f"Your home energy data is verified. This action specifically targets your baseline footprint, potentially saving {round(abs(co2e_saved_t), 2)} tCO₂e."
        else:
             why = f"Based on your footprint, this action provides an estimated savings of {round(abs(co2e_saved_t), 2)} tCO₂e."

        return RankedAction(
            id=template.id,
            title=template.title,
            description=template.description,
            category=template.category,
            co2e_saved_per_year=round(abs(co2e_saved_t), 3),
            effort_score=template.base_effort_score,
            impact_score=impact_score,
            composite_score=composite,
            upfront_cost_usd=template.upfront_cost_usd,
            annual_saving_usd=template.annual_saving_usd,
            time_to_impact_days=template.time_to_impact_days,
            co_benefits=co_benefits,
            why_recommended=why,
            is_feasible=feasible,
            feasibility_reason=None if feasible else "Not available based on your living situation",
        )
