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

from app.data.action_catalogue import ACTION_CATALOGUE, ActionTemplate
from app.models.actions import RankedAction, UserConstraints
from app.models.carbon import CarbonInventory, CarbonProfile
from app.models.simulation import CoBenefit


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
            if not a.is_relevant(inventory):
                continue
            if not a.is_allowed(constraints):
                continue
            if a.category.value in constraints.exclude_categories:
                continue

            if a.category.value == "diet" and profile.diet is None:
                continue
            if a.category.value == "transport" and profile.transport is None:
                continue
            if a.category.value == "consumption" and profile.consumption is None:
                continue
            if a.category.value == "home" and profile.home is None:
                continue
            if a.category.value == "digital" and profile.digital is None:
                continue

            stype = a.scenario_type
            if (
                stype == "switch_diet"
                and profile.diet
                and profile.diet.diet_type.value == a.scenario_params.get("new_diet")
            ):
                continue
            if (
                stype == "switch_car"
                and profile.transport
                and profile.transport.car
                and profile.transport.car.car_type.value == a.scenario_params.get("new_car_type")
            ):
                continue
            if (
                stype == "switch_heating"
                and profile.home
                and profile.home.heating_type.value == a.scenario_params.get("new_heating_type")
            ):
                continue
            if (
                stype == "add_renewable"
                and profile.home
                and profile.home.renewable_tariff
                and a.scenario_params.get("switch_to_renewable_tariff")
            ):
                continue
            if (
                stype == "extend_devices"
                and profile.digital
                and profile.digital.device_upgrade_frequency.value
                == a.scenario_params.get("new_device_frequency")
            ):
                continue
            if (
                stype == "reduce_streaming"
                and profile.digital
                and profile.digital.streaming_gaming_usage.value
                == a.scenario_params.get("new_streaming_usage")
            ):
                continue

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

        speed = self.WEIGHTS["speed"] * normalise_speed(template.time_to_impact_days)
        coben = self.WEIGHTS["coben"] * min(len(co_benefits) * 0.05, 0.05)

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
        impact_score = min(
            5, max(1, round(normalise_impact(co2e_saved_t * 1000, total_footprint_kg) * 5))
        )

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
