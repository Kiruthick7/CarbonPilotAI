from typing import Any

from app.models.carbon import CarbonProfile


class DietCalculator:
    @staticmethod
    def compute(profile: CarbonProfile, emission_factors: dict[str, Any], food_waste_multipliers: dict[str, float]) -> dict[str, float]:
        if not profile.diet:
            return {"total": 0.0, "base": 0.0, "waste": 0.0}
        f = emission_factors
        d = profile.diet
        base_per_day = f[d.diet_type.value]["kgCO2e_per_day"]
        waste_mult = food_waste_multipliers.get(d.food_waste.value, 1.0)
        base_kg = base_per_day * 365
        total_kg = base_kg * waste_mult
        waste_kg = total_kg - base_kg
        return {"total": total_kg, "base": base_kg, "waste": waste_kg}
