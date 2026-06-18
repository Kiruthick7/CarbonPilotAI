"""
carbon_engine.py — Revised to match existing Pydantic model field names.
Pure computation engine. Stateless. Converts CarbonProfile → CarbonInventory.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import structlog

from app.models.carbon import (
    CalculationTrace,
    CarbonInventory,
    CarbonProfile,
    CategoryBreakdown,
    SubcategoryItem,
)

logger = structlog.get_logger(__name__)

from app.engines.calculators.constants import GLOBAL_15C_BUDGET, GLOBAL_GRID_FALLBACK
from app.engines.calculators.consumption_calculator import ConsumptionCalculator
from app.engines.calculators.diet_calculator import DietCalculator
from app.engines.calculators.digital_calculator import DigitalCalculator
from app.engines.calculators.home_calculator import HomeCalculator
from app.engines.calculators.transport_calculator import TransportCalculator


@dataclass(frozen=True)
class EmissionFactors:
    """Immutable container for all emission factor data."""

    transport: dict[str, Any]
    diet: dict[str, Any]
    food_waste_multipliers: dict[str, float]
    home: dict[str, Any]
    consumption: dict[str, Any]
    version: str
    grid_intensity: dict[str, float]
    benchmarks: dict[str, Any]


class CarbonEngine:
    """
    Stateless carbon footprint calculator.
    Single responsibility: CarbonProfile → CarbonInventory.
    """

    def __init__(self, factors: EmissionFactors) -> None:
        self._f = factors

    @property
    def version(self) -> str:
        return self._f.version

    def compute(self, profile: CarbonProfile) -> CarbonInventory:
        transport_kg = TransportCalculator.compute(
            profile, self._f.transport, self._f.grid_intensity
        )
        diet_kg = DietCalculator.compute(profile, self._f.diet, self._f.food_waste_multipliers)
        home_kg = HomeCalculator.compute(profile, self._f.home, self._f.grid_intensity)
        consumption_kg = ConsumptionCalculator.compute(profile, self._f.consumption)
        digital_kg = DigitalCalculator.compute(profile)

        transport_total = transport_kg["total"]
        diet_total = diet_kg["total"]
        home_total = home_kg["total"]
        consumption_total = consumption_kg["total"]
        digital_total = digital_kg["total"]

        grand_total_kg = (
            transport_total + diet_total + home_total + consumption_total + digital_total
        )
        grand_total_t = grand_total_kg / 1000

        transport_breakdown = CategoryBreakdown(
            category="transport",
            total_kgco2e=round(transport_total, 1),
            subcategories=[
                SubcategoryItem(
                    label="Car",
                    kgco2e=round(transport_kg["car"], 1),
                    share_of_category=round(transport_kg["car"] / max(transport_total, 1), 3),
                ),
                SubcategoryItem(
                    label="Short-haul flights",
                    kgco2e=round(transport_kg["short_haul"], 1),
                    share_of_category=round(
                        transport_kg["short_haul"] / max(transport_total, 1), 3
                    ),
                ),
                SubcategoryItem(
                    label="Long-haul flights",
                    kgco2e=round(transport_kg["long_haul"], 1),
                    share_of_category=round(transport_kg["long_haul"] / max(transport_total, 1), 3),
                ),
                SubcategoryItem(
                    label="Public transport",
                    kgco2e=round(transport_kg["public"], 1),
                    share_of_category=round(transport_kg["public"] / max(transport_total, 1), 3),
                ),
            ],
        )

        diet_breakdown = CategoryBreakdown(
            category="diet",
            total_kgco2e=round(diet_total, 1),
            subcategories=[
                SubcategoryItem(
                    label="Food production",
                    kgco2e=round(diet_kg["base"], 1),
                    share_of_category=round(diet_kg["base"] / max(diet_total, 1), 3),
                ),
                SubcategoryItem(
                    label="Food waste",
                    kgco2e=round(diet_kg["waste"], 1),
                    share_of_category=round(diet_kg["waste"] / max(diet_total, 1), 3),
                ),
            ],
        )

        home_breakdown = CategoryBreakdown(
            category="home",
            total_kgco2e=round(home_total, 1),
            subcategories=[
                SubcategoryItem(
                    label="Heating",
                    kgco2e=round(home_kg["heating"], 1),
                    share_of_category=round(home_kg["heating"] / max(home_total, 1), 3),
                ),
                SubcategoryItem(
                    label="Electricity",
                    kgco2e=round(home_kg["electricity"], 1),
                    share_of_category=round(home_kg["electricity"] / max(home_total, 1), 3),
                ),
            ],
        )

        consumption_breakdown = CategoryBreakdown(
            category="consumption",
            total_kgco2e=round(consumption_total, 1),
            subcategories=[
                SubcategoryItem(
                    label="Clothing",
                    kgco2e=round(consumption_kg["clothing"], 1),
                    share_of_category=round(
                        consumption_kg["clothing"] / max(consumption_total, 1), 3
                    ),
                ),
                SubcategoryItem(
                    label="Electronics",
                    kgco2e=round(consumption_kg["electronics"], 1),
                    share_of_category=round(
                        consumption_kg["electronics"] / max(consumption_total, 1), 3
                    ),
                ),
                SubcategoryItem(
                    label="Deliveries",
                    kgco2e=round(consumption_kg["deliveries"], 1),
                    share_of_category=round(
                        consumption_kg["deliveries"] / max(consumption_total, 1), 3
                    ),
                ),
            ],
        )

        digital_breakdown = CategoryBreakdown(
            category="digital",
            total_kgco2e=round(digital_total, 1),
            subcategories=[
                SubcategoryItem(
                    label="Embodied (Hardware)",
                    kgco2e=round(digital_kg["hardware"], 1),
                    share_of_category=round(digital_kg["hardware"] / max(digital_total, 1), 3),
                ),
                SubcategoryItem(
                    label="Operational (Streaming & AI)",
                    kgco2e=round(digital_kg["operational"], 1),
                    share_of_category=round(digital_kg["operational"] / max(digital_total, 1), 3),
                ),
            ],
        )

        national_avg = self._f.benchmarks.get("national_averages", {}).get(
            profile.country_code,
            self._f.benchmarks.get("global_average_tco2e", 4.8),
        )

        trace = CalculationTrace(
            formula="(transport + diet + home + consumption + digital) / 1000",
            variables={
                "transport_kg": str(round(transport_total, 1)),
                "diet_kg": str(round(diet_total, 1)),
                "home_kg": str(round(home_total, 1)),
                "consumption_kg": str(round(consumption_total, 1)),
                "digital_kg": str(round(digital_total, 1)),
            },
            source="CarbonPilot Deterministic Engine v" + self._f.version,
        )

        return CarbonInventory(
            total_tco2e=round(grand_total_t, 3),
            breakdowns=[
                transport_breakdown,
                diet_breakdown,
                home_breakdown,
                consumption_breakdown,
                digital_breakdown,
            ],
            national_average_tco2e=national_avg,
            global_average_tco2e=4.8,
            budget_1_5c_tco2e=GLOBAL_15C_BUDGET,
            trace=trace,
        )

    def compute_percentile(self, total_t: float, national_avg_t: float) -> float:
        if national_avg_t <= 0:
            return 50.0
        ratio = total_t / national_avg_t
        percentile = 100 * (1 / (1 + math.exp(-2.0 * (ratio - 1.0))))
        return round(min(max(percentile, 1.0), 99.0), 1)

    def get_factors_used(self, profile: CarbonProfile) -> list[dict[str, str]]:
        grid = self._f.grid_intensity.get(profile.country_code, GLOBAL_GRID_FALLBACK)
        return [
            {"category": "transport.car", "source": "DEFRA 2023", "unit": "kgCO2e/km"},
            {
                "category": "transport.flights",
                "source": "IPCC AR6",
                "unit": "kgCO2e/flight + RF×1.9",
            },
            {"category": "diet", "source": "Poore & Nemecek 2018", "unit": "kgCO2e/day"},
            {
                "category": "home.grid",
                "source": "IEA 2023",
                "unit": f"{grid} kgCO2e/kWh ({profile.country_code})",
            },
            {"category": "consumption", "source": "EPA 2023", "unit": "kgCO2e/item"},
            {
                "category": "digital",
                "source": "Industry Averages",
                "unit": "kgCO2e/lifecycle + kgCO2e/hr",
            },
        ]
