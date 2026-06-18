from typing import Any

from app.engines.calculators.constants import GLOBAL_GRID_FALLBACK, RADIATIVE_FORCING
from app.models.carbon import CarbonProfile, CarType


class TransportCalculator:
    @staticmethod
    def compute(
        profile: CarbonProfile,
        emission_factors: dict[str, Any],
        grid_intensity_map: dict[str, float],
    ) -> dict[str, float]:
        if not profile.transport:
            return {"total": 0.0, "car": 0.0, "short_haul": 0.0, "long_haul": 0.0, "public": 0.0}
        f = emission_factors
        grid = grid_intensity_map.get(profile.country_code, GLOBAL_GRID_FALLBACK)
        t = profile.transport

        car_kg = 0.0
        if t.car:
            if t.car.car_type == CarType.ELECTRIC:
                wh_per_km = f["car"]["electric"]["wh_per_km"]
                car_kg = t.car.weekly_km * 52 * (wh_per_km / 1000) * grid
            elif t.car.car_type != CarType.NONE:
                car_kg = t.car.weekly_km * 52 * f["car"][t.car.car_type.value]["kgCO2e_per_km"]

        short_haul_kg = (
            t.flights.short_haul_flights * f["flights"]["short_haul_kg"] * RADIATIVE_FORCING
        )
        long_haul_kg = (
            t.flights.long_haul_flights * f["flights"]["long_haul_kg"] * RADIATIVE_FORCING
        )

        bus_km = t.weekly_public_transport_km * 52 * t.public_transport_split_bus
        train_km = t.weekly_public_transport_km * 52 * (1 - t.public_transport_split_bus)
        public_kg = bus_km * f["bus"]["kgCO2e_per_km"] + train_km * f["train"]["kgCO2e_per_km"]

        total = car_kg + short_haul_kg + long_haul_kg + public_kg
        return {
            "total": total,
            "car": car_kg,
            "short_haul": short_haul_kg,
            "long_haul": long_haul_kg,
            "public": public_kg,
        }
