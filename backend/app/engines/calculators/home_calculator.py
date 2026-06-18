from typing import Any

from app.engines.calculators.constants import GLOBAL_GRID_FALLBACK
from app.models.carbon import CarbonProfile


class HomeCalculator:
    @staticmethod
    def compute(profile: CarbonProfile, emission_factors: dict[str, Any], grid_intensity_map: dict[str, float]) -> dict[str, float]:
        fh = emission_factors
        h = profile.home
        grid = grid_intensity_map.get(profile.country_code, GLOBAL_GRID_FALLBACK)

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
