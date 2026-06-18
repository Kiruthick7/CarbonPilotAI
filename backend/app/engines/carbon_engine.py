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
    CarType,
    CategoryBreakdown,
    SubcategoryItem,
)

logger = structlog.get_logger(__name__)

GLOBAL_GRID_FALLBACK = 0.386
GLOBAL_15C_BUDGET = 2.3
RADIATIVE_FORCING = 1.9


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
        transport_kg = self._compute_transport_kg(profile)
        diet_kg = self._compute_diet_kg(profile)
        home_kg = self._compute_home_kg(profile)
        consumption_kg = self._compute_consumption_kg(profile)
        digital_kg = self._compute_digital_kg(profile)

        transport_total = transport_kg["total"]
        diet_total = diet_kg["total"]
        home_total = home_kg["total"]
        consumption_total = consumption_kg["total"]
        digital_total = digital_kg["total"]

        grand_total_kg = transport_total + diet_total + home_total + consumption_total + digital_total
        grand_total_t = grand_total_kg / 1000


        transport_breakdown = CategoryBreakdown(
            category="transport",
            total_kgco2e=round(transport_total, 1),
            subcategories=[
                SubcategoryItem(label="Car", kgco2e=round(transport_kg["car"], 1), share_of_category=round(transport_kg["car"] / max(transport_total, 1), 3)),
                SubcategoryItem(label="Short-haul flights", kgco2e=round(transport_kg["short_haul"], 1), share_of_category=round(transport_kg["short_haul"] / max(transport_total, 1), 3)),
                SubcategoryItem(label="Long-haul flights", kgco2e=round(transport_kg["long_haul"], 1), share_of_category=round(transport_kg["long_haul"] / max(transport_total, 1), 3)),
                SubcategoryItem(label="Public transport", kgco2e=round(transport_kg["public"], 1), share_of_category=round(transport_kg["public"] / max(transport_total, 1), 3)),
            ],
        )

        diet_breakdown = CategoryBreakdown(
            category="diet",
            total_kgco2e=round(diet_total, 1),
            subcategories=[
                SubcategoryItem(label="Food production", kgco2e=round(diet_kg["base"], 1), share_of_category=round(diet_kg["base"] / max(diet_total, 1), 3)),
                SubcategoryItem(label="Food waste", kgco2e=round(diet_kg["waste"], 1), share_of_category=round(diet_kg["waste"] / max(diet_total, 1), 3)),
            ],
        )

        home_breakdown = CategoryBreakdown(
            category="home",
            total_kgco2e=round(home_total, 1),
            subcategories=[
                SubcategoryItem(label="Heating", kgco2e=round(home_kg["heating"], 1), share_of_category=round(home_kg["heating"] / max(home_total, 1), 3)),
                SubcategoryItem(label="Electricity", kgco2e=round(home_kg["electricity"], 1), share_of_category=round(home_kg["electricity"] / max(home_total, 1), 3)),
            ],
        )

        consumption_breakdown = CategoryBreakdown(
            category="consumption",
            total_kgco2e=round(consumption_total, 1),
            subcategories=[
                SubcategoryItem(label="Clothing", kgco2e=round(consumption_kg["clothing"], 1), share_of_category=round(consumption_kg["clothing"] / max(consumption_total, 1), 3)),
                SubcategoryItem(label="Electronics", kgco2e=round(consumption_kg["electronics"], 1), share_of_category=round(consumption_kg["electronics"] / max(consumption_total, 1), 3)),
                SubcategoryItem(label="Deliveries", kgco2e=round(consumption_kg["deliveries"], 1), share_of_category=round(consumption_kg["deliveries"] / max(consumption_total, 1), 3)),
            ],
        )

        digital_breakdown = CategoryBreakdown(
            category="digital",
            total_kgco2e=round(digital_total, 1),
            subcategories=[
                SubcategoryItem(label="Embodied (Hardware)", kgco2e=round(digital_kg["hardware"], 1), share_of_category=round(digital_kg["hardware"] / max(digital_total, 1), 3)),
                SubcategoryItem(label="Operational (Streaming & AI)", kgco2e=round(digital_kg["operational"], 1), share_of_category=round(digital_kg["operational"] / max(digital_total, 1), 3)),
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
                "digital_kg": str(round(digital_total, 1))
            },
            source="CarbonPilot Deterministic Engine v" + self._f.version
        )

        return CarbonInventory(
            total_tco2e=round(grand_total_t, 3),
            breakdowns=[transport_breakdown, diet_breakdown, home_breakdown, consumption_breakdown, digital_breakdown],
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

    def _compute_transport_kg(self, profile: CarbonProfile) -> dict[str, float]:
        if not profile.transport:
            return {"total": 0.0, "car": 0.0, "short_haul": 0.0, "long_haul": 0.0, "public": 0.0}
        f = self._f.transport
        grid = self._f.grid_intensity.get(profile.country_code, GLOBAL_GRID_FALLBACK)
        t = profile.transport

        car_kg = 0.0
        if t.car:
            if t.car.car_type == CarType.ELECTRIC:
                wh_per_km = f["car"]["electric"]["wh_per_km"]
                car_kg = t.car.weekly_km * 52 * (wh_per_km / 1000) * grid
            elif t.car.car_type != CarType.NONE:
                car_kg = t.car.weekly_km * 52 * f["car"][t.car.car_type.value]["kgCO2e_per_km"]

        short_haul_kg = t.flights.short_haul_flights * f["flights"]["short_haul_kg"] * RADIATIVE_FORCING
        long_haul_kg = t.flights.long_haul_flights * f["flights"]["long_haul_kg"] * RADIATIVE_FORCING

        bus_km = t.weekly_public_transport_km * 52 * t.public_transport_split_bus
        train_km = t.weekly_public_transport_km * 52 * (1 - t.public_transport_split_bus)
        public_kg = bus_km * f["bus"]["kgCO2e_per_km"] + train_km * f["train"]["kgCO2e_per_km"]

        total = car_kg + short_haul_kg + long_haul_kg + public_kg
        return {"total": total, "car": car_kg, "short_haul": short_haul_kg, "long_haul": long_haul_kg, "public": public_kg}

    def _compute_diet_kg(self, profile: CarbonProfile) -> dict[str, float]:
        if not profile.diet:
            return {"total": 0.0, "base": 0.0, "waste": 0.0}
        f = self._f.diet
        d = profile.diet
        base_per_day = f[d.diet_type.value]["kgCO2e_per_day"]
        waste_mult = self._f.food_waste_multipliers.get(d.food_waste.value, 1.0)
        base_kg = base_per_day * 365
        total_kg = base_kg * waste_mult
        waste_kg = total_kg - base_kg
        return {"total": total_kg, "base": base_kg, "waste": waste_kg}

    def _compute_home_kg(self, profile: CarbonProfile) -> dict[str, float]:
        fh = self._f.home
        h = profile.home
        grid = self._f.grid_intensity.get(profile.country_code, GLOBAL_GRID_FALLBACK)

        kwh = fh["heating_kwh_per_year"][h.home_size.value]
        heat_factor = fh["heating"][h.heating_type.value]

        if heat_factor.get("kgCO2e_per_kwh") == "grid":
            heating_kg = kwh * grid
        elif h.heating_type.value == "heat_pump":
            heating_kg = (kwh / heat_factor.get("cop", 3.0)) * grid
        else:
            heating_kg = kwh * heat_factor["kgCO2e_per_kwh"]

        elec_kwh = fh["electricity_kwh_defaults"][h.home_size.value]
        elec_mult = fh["renewable_electricity_multiplier"] if (h.renewable_tariff or h.has_solar) else 1.0
        electricity_kg = elec_kwh * grid * elec_mult

        per_person_heating = heating_kg / max(h.num_occupants, 1)
        per_person_elec = electricity_kg / max(h.num_occupants, 1)
        total = per_person_heating + per_person_elec

        return {"total": total, "heating": per_person_heating, "electricity": per_person_elec}

    def _compute_consumption_kg(self, profile: CarbonProfile) -> dict[str, float]:
        if not profile.consumption:
            return {"total": 0.0, "clothing": 0.0, "electronics": 0.0, "deliveries": 0.0}
        fc = self._f.consumption
        c = profile.consumption
        clothing = c.new_clothing_items_per_year * fc["clothing_per_item_kg"]
        electronics = c.new_electronics_per_year * fc["electronics_per_device_kg"]
        deliveries = c.online_deliveries_per_week * 52 * fc["delivery_per_order_kg"]
        return {"total": clothing + electronics + deliveries, "clothing": clothing, "electronics": electronics, "deliveries": deliveries}

    def _compute_digital_kg(self, profile: CarbonProfile) -> dict[str, float]:
        if not profile.digital:
            return {"total": 0.0, "hardware": 0.0, "operational": 0.0}
        d = profile.digital

        # Hardware Embodied Carbon (Phone ~70kg, Laptop ~300kg)
        hw_emissions = {"frequent": 1.5, "average": 3.5, "rare": 5.0} # Lifespan in years
        lifespan = hw_emissions.get(d.device_upgrade_frequency.value, 3.5)
        hardware = (70.0 / lifespan) + (300.0 / lifespan)

        # Operational: Streaming & Gaming (0.05kg CO2e per hr)
        # Light: 0.5hr/day, Moderate: 3hr/day, Heavy: 6hr/day
        stream_hours = {"light": 0.5, "moderate": 3.0, "heavy": 6.0}
        streaming_kg = stream_hours.get(d.streaming_gaming_usage.value, 3.0) * 365 * 0.05

        # Operational: AI & Cloud Usage (LLM query ~0.005g, Image ~2g) -> Avg 0.01kg per heavy day
        ai_days = {"rare": 0.001, "occasional": 0.005, "heavy": 0.02}
        ai_kg = ai_days.get(d.ai_cloud_usage.value, 0.005) * 365

        operational = streaming_kg + ai_kg
        return {"total": hardware + operational, "hardware": hardware, "operational": operational}

    def get_factors_used(self, profile: CarbonProfile) -> list[dict[str, str]]:
        grid = self._f.grid_intensity.get(profile.country_code, GLOBAL_GRID_FALLBACK)
        return [
            {"category": "transport.car", "source": "DEFRA 2023", "unit": "kgCO2e/km"},
            {"category": "transport.flights", "source": "IPCC AR6", "unit": "kgCO2e/flight + RF×1.9"},
            {"category": "diet", "source": "Poore & Nemecek 2018", "unit": "kgCO2e/day"},
            {"category": "home.grid", "source": "IEA 2023", "unit": f"{grid} kgCO2e/kWh ({profile.country_code})"},
            {"category": "consumption", "source": "EPA 2023", "unit": "kgCO2e/item"},
            {"category": "digital", "source": "Industry Averages", "unit": "kgCO2e/lifecycle + kgCO2e/hr"},
        ]
