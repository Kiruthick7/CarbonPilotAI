"""
simulation_engine.py — Python 3.9 compatible (no match/case).
Pure scenario delta engine. No I/O.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.models.carbon import (
    CarbonInventory,
    CarbonProfile,
    CarType,
    DietType,
    HeatingType,
)
from app.models.simulation import (
    AddRenewableParams,
    CoBenefit,
    CoBenefitType,
    ExtendDevicesParams,
    ReduceConsumptionParams,
    ReduceFlightsParams,
    ReduceStreamingParams,
    Scenario,
    ScenarioType,
    SimulateResponse,
    SwitchCarParams,
    SwitchDietParams,
    SwitchHeatingParams,
)


class SimulationEngine:
    """Applies a Scenario to a CarbonProfile to produce a modified profile."""

    def __init__(self) -> None:
        self._scenario_handlers: dict[ScenarioType, Callable[[dict[str, Any], Any], None]] = {
            ScenarioType.SWITCH_DIET: self._handle_switch_diet,
            ScenarioType.SWITCH_CAR: self._handle_switch_car,
            ScenarioType.REDUCE_FLIGHTS: self._handle_reduce_flights,
            ScenarioType.SWITCH_HEATING: self._handle_switch_heating,
            ScenarioType.ADD_RENEWABLE: self._handle_add_renewable,
            ScenarioType.REDUCE_CONSUMPTION: self._handle_reduce_consumption,
            ScenarioType.EXTEND_DEVICES: self._handle_extend_devices,
            ScenarioType.REDUCE_STREAMING: self._handle_reduce_streaming,
        }

    def apply_scenario(self, profile: CarbonProfile, scenario: Scenario) -> CarbonProfile:
        """Return a new CarbonProfile with the scenario change applied."""
        data = profile.model_dump()
        handler = self._scenario_handlers.get(scenario.type)
        if handler:
            handler(data, scenario)
        return CarbonProfile.model_validate(data)

    def _handle_switch_diet(self, data: dict[str, Any], scenario: Any) -> None:
        if isinstance(scenario, SwitchDietParams) and data.get("diet"):
            data["diet"]["diet_type"] = scenario.new_diet.value

    def _handle_switch_car(self, data: dict[str, Any], scenario: Any) -> None:
        if (
            isinstance(scenario, SwitchCarParams)
            and data.get("transport")
            and data["transport"].get("car")
        ):
            data["transport"]["car"]["car_type"] = scenario.new_car_type.value
            if scenario.new_car_type == CarType.NONE:
                data["transport"]["car"] = None

    def _handle_reduce_flights(self, data: dict[str, Any], scenario: Any) -> None:
        if (
            isinstance(scenario, ReduceFlightsParams)
            and data.get("transport")
            and data["transport"].get("flights")
        ):
            flights = data["transport"]["flights"]
            flights["short_haul_flights"] = max(
                0, flights["short_haul_flights"] - scenario.reduce_short_haul_by
            )
            flights["long_haul_flights"] = max(
                0, flights["long_haul_flights"] - scenario.reduce_long_haul_by
            )

    def _handle_switch_heating(self, data: dict[str, Any], scenario: Any) -> None:
        if isinstance(scenario, SwitchHeatingParams) and data.get("home"):
            data["home"]["heating_type"] = scenario.new_heating_type.value

    def _handle_add_renewable(self, data: dict[str, Any], scenario: Any) -> None:
        if isinstance(scenario, AddRenewableParams) and data.get("home"):
            data["home"]["renewable_tariff"] = scenario.switch_to_renewable_tariff
            data["home"]["has_solar"] = scenario.add_solar_panels

    def _handle_reduce_consumption(self, data: dict[str, Any], scenario: Any) -> None:
        if isinstance(scenario, ReduceConsumptionParams) and data.get("consumption"):
            data["consumption"]["new_clothing_items_per_year"] = max(
                0, data["consumption"]["new_clothing_items_per_year"] - scenario.reduce_clothing_by
            )
            data["consumption"]["new_electronics_per_year"] = max(
                0, data["consumption"]["new_electronics_per_year"] - scenario.reduce_electronics_by
            )
            data["consumption"]["online_deliveries_per_week"] = max(
                0.0,
                data["consumption"]["online_deliveries_per_week"] - scenario.reduce_deliveries_by,
            )

    def _handle_extend_devices(self, data: dict[str, Any], scenario: Any) -> None:
        if isinstance(scenario, ExtendDevicesParams) and data.get("digital"):
            data["digital"]["device_upgrade_frequency"] = scenario.new_device_frequency.value

    def _handle_reduce_streaming(self, data: dict[str, Any], scenario: Any) -> None:
        if isinstance(scenario, ReduceStreamingParams) and data.get("digital"):
            data["digital"]["streaming_gaming_usage"] = scenario.new_streaming_usage.value

    def compute_delta(
        self,
        original: CarbonInventory,
        new: CarbonInventory,
        scenario: Scenario | None = None,
        scenarios: list[Scenario] | None = None,
    ) -> SimulateResponse:
        delta = round(new.total_tco2e - original.total_tco2e, 3)
        delta_pct = round(
            (delta / original.total_tco2e * 100) if original.total_tco2e > 0 else 0.0,
            1,
        )

        all_scenarios = scenarios or []
        if scenario and scenario not in all_scenarios:
            all_scenarios.append(scenario)

        co_benefits: list[CoBenefit] = []
        total_upfront = 0.0
        total_annual_saving = 0.0
        applied_scenarios: list[str] = []

        for sc in all_scenarios:
            applied_scenarios.append(sc.type.value)
            co_benefits.extend(self._derive_co_benefits(sc, delta))
            _, upfront, annual = self._financial_model(sc, delta)
            if upfront:
                total_upfront += upfront
            if annual:
                total_annual_saving += annual

        years_bev = (
            round(total_upfront / total_annual_saving, 1) if total_annual_saving > 0 else None
        )

        return SimulateResponse(
            original_total=original.total_tco2e,
            new_total=new.total_tco2e,
            delta_co2e=delta,
            delta_percent=delta_pct,
            new_inventory=new,
            years_to_break_even=years_bev,
            upfront_cost_usd=total_upfront if total_upfront > 0 else None,
            annual_saving_usd=total_annual_saving if total_annual_saving > 0 else None,
            co_benefits=co_benefits,
            applied_scenarios=applied_scenarios,
        )

    @staticmethod
    def _derive_co_benefits(scenario: Scenario, delta: float) -> list[CoBenefit]:
        stype = scenario.type
        benefits: list[CoBenefit] = []

        if stype == ScenarioType.SWITCH_DIET and isinstance(scenario, SwitchDietParams):
            if scenario.new_diet in (DietType.VEGAN, DietType.VEGETARIAN):
                benefits.append(
                    CoBenefit(
                        type=CoBenefitType.HEALTH,
                        description="Reduced risk of heart disease and type-2 diabetes",
                    )
                )
                benefits.append(
                    CoBenefit(
                        type=CoBenefitType.FINANCIAL,
                        description="Plant-based diets typically save $1,200–$1,800/year on food",
                        quantified="~$1,500/year",
                    )
                )

        elif stype == ScenarioType.SWITCH_CAR and isinstance(scenario, SwitchCarParams):
            if scenario.new_car_type == CarType.ELECTRIC:
                benefits.append(
                    CoBenefit(
                        type=CoBenefitType.FINANCIAL,
                        description="Lower fuel and maintenance costs vs petrol",
                        quantified="~$1,000–2,000/year",
                    )
                )
                benefits.append(
                    CoBenefit(
                        type=CoBenefitType.AIR_QUALITY,
                        description="Zero tailpipe emissions improves local air quality",
                    )
                )

        elif stype == ScenarioType.REDUCE_FLIGHTS and isinstance(scenario, ReduceFlightsParams):
            benefits.append(
                CoBenefit(
                    type=CoBenefitType.FINANCIAL,
                    description="Significant cost savings on flights",
                    quantified=f"~${abs(int(delta * 300))}/year saved",
                )
            )

        elif stype == ScenarioType.SWITCH_HEATING and isinstance(scenario, SwitchHeatingParams):
            if scenario.new_heating_type == HeatingType.HEAT_PUMP:
                benefits.append(
                    CoBenefit(
                        type=CoBenefitType.FINANCIAL,
                        description="Lower running costs than gas in most climates",
                        quantified="~$500–800/year once installed",
                    )
                )

        elif stype == ScenarioType.EXTEND_DEVICES and isinstance(scenario, ExtendDevicesParams):
            benefits.append(
                CoBenefit(
                    type=CoBenefitType.FINANCIAL,
                    description="Save thousands by delaying hardware upgrades",
                    quantified="~$300–800/year",
                )
            )

        return benefits

    @staticmethod
    def _financial_model(
        scenario: Scenario, delta: float
    ) -> tuple[float | None, float | None, float | None]:
        stype = scenario.type
        if stype == ScenarioType.SWITCH_CAR and isinstance(scenario, SwitchCarParams):
            upfront = getattr(scenario, "upfront_cost_usd", None) or 8_000.0
            annual = 1_500.0
            return round(upfront / annual, 1), upfront, annual
        if stype == ScenarioType.SWITCH_HEATING and isinstance(scenario, SwitchHeatingParams):
            upfront = getattr(scenario, "upfront_cost_usd", None) or 12_000.0
            annual = 700.0
            return round(upfront / annual, 1), upfront, annual
        return None, None, None
