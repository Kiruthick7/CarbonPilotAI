"""Pydantic v2 models for the what-if simulation endpoint.

Each ``ScenarioType`` has a dedicated params model. The ``Scenario`` union uses
the ``type`` field as a discriminator so FastAPI / Pydantic can deserialise the
correct sub-model automatically.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal


class StrEnum(str, Enum):
    """Python 3.9-compatible StrEnum substitute."""

    pass


from pydantic import BaseModel, Field

from app.models.carbon import (
    CarbonInventory,
    CarbonProfile,
    CarType,
    DailyUsage,
    DeviceFrequency,
    DietType,
    HeatingType,
)


class ScenarioType(StrEnum):
    """All supported what-if scenario types."""

    SWITCH_DIET = "switch_diet"
    SWITCH_CAR = "switch_car"
    REDUCE_FLIGHTS = "reduce_flights"
    SWITCH_HEATING = "switch_heating"
    ADD_RENEWABLE = "add_renewable"
    REDUCE_CONSUMPTION = "reduce_consumption"
    EXTEND_DEVICES = "extend_devices"
    REDUCE_STREAMING = "reduce_streaming"


class SwitchDietParams(BaseModel):
    """Parameters for switching to a lower-carbon dietary pattern."""

    type: Literal[ScenarioType.SWITCH_DIET] = ScenarioType.SWITCH_DIET
    new_diet: DietType = Field(..., description="Target dietary pattern.")


class SwitchCarParams(BaseModel):
    """Parameters for switching to a different vehicle type."""

    type: Literal[ScenarioType.SWITCH_CAR] = ScenarioType.SWITCH_CAR
    new_car_type: CarType = Field(..., description="Target vehicle fuel / propulsion type.")
    upfront_cost_usd: Annotated[float, Field(ge=0.0, le=200_000.0)] | None = Field(
        default=None, description="Optional estimated purchase cost in USD."
    )


class ReduceFlightsParams(BaseModel):
    """Parameters for reducing annual flight activity."""

    type: Literal[ScenarioType.REDUCE_FLIGHTS] = ScenarioType.REDUCE_FLIGHTS
    reduce_short_haul_by: Annotated[int, Field(ge=0, le=365)] = Field(
        default=0, description="Number of short-haul return trips to eliminate."
    )
    reduce_long_haul_by: Annotated[int, Field(ge=0, le=52)] = Field(
        default=0, description="Number of long-haul return trips to eliminate."
    )


class SwitchHeatingParams(BaseModel):
    """Parameters for switching to a different home heating system."""

    type: Literal[ScenarioType.SWITCH_HEATING] = ScenarioType.SWITCH_HEATING
    new_heating_type: HeatingType = Field(..., description="Target heating system.")
    upfront_cost_usd: Annotated[float, Field(ge=0.0, le=100_000.0)] | None = Field(
        default=None, description="Optional installation cost in USD."
    )


class AddRenewableParams(BaseModel):
    """Parameters for switching to a renewable electricity tariff or solar."""

    type: Literal[ScenarioType.ADD_RENEWABLE] = ScenarioType.ADD_RENEWABLE
    switch_to_renewable_tariff: bool = Field(
        default=True, description="Switch to a 100 % renewable electricity tariff."
    )
    add_solar_panels: bool = Field(default=False, description="Add rooftop solar panels.")
    upfront_cost_usd: Annotated[float, Field(ge=0.0, le=50_000.0)] | None = Field(
        default=None, description="Optional installation cost for solar (USD)."
    )


class ReduceConsumptionParams(BaseModel):
    """Parameters for reducing discretionary consumption."""

    type: Literal[ScenarioType.REDUCE_CONSUMPTION] = ScenarioType.REDUCE_CONSUMPTION
    reduce_clothing_by: Annotated[int, Field(ge=0, le=500)] = Field(
        default=0, description="Number of clothing items to stop buying per year."
    )
    reduce_electronics_by: Annotated[int, Field(ge=0, le=50)] = Field(
        default=0, description="Number of electronic devices to stop buying per year."
    )
    reduce_deliveries_by: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        default=0.0, description="Weekly online delivery orders to eliminate."
    )


class ExtendDevicesParams(BaseModel):
    """Parameters for extending device lifespan."""

    type: Literal[ScenarioType.EXTEND_DEVICES] = ScenarioType.EXTEND_DEVICES
    new_device_frequency: DeviceFrequency = Field(
        ..., description="Target device upgrade frequency."
    )


class ReduceStreamingParams(BaseModel):
    """Parameters for reducing streaming quality or hours."""

    type: Literal[ScenarioType.REDUCE_STREAMING] = ScenarioType.REDUCE_STREAMING
    new_streaming_usage: DailyUsage = Field(..., description="Target streaming usage.")


Scenario = Annotated[
    SwitchDietParams
    | SwitchCarParams
    | ReduceFlightsParams
    | SwitchHeatingParams
    | AddRenewableParams
    | ReduceConsumptionParams
    | ExtendDevicesParams
    | ReduceStreamingParams,
    Field(discriminator="type"),
]
"""Union of all scenario param models, discriminated on the ``type`` field."""


class CoBenefitType(StrEnum):
    """Non-carbon positive side-effects of an action or scenario."""

    HEALTH = "health"
    FINANCIAL = "financial"
    AIR_QUALITY = "air_quality"
    NOISE = "noise"


class CoBenefit(BaseModel):
    """A non-carbon benefit associated with a scenario or action."""

    type: CoBenefitType = Field(..., description="Category of co-benefit.")
    description: str = Field(
        ..., min_length=1, max_length=500, description="Human-readable explanation."
    )
    quantified: str | None = Field(
        default=None, description="Quantified value, e.g. '~$1,500/year'."
    )


class SimulateRequest(BaseModel):
    """Request body for ``POST /simulate``."""

    inventory: CarbonInventory = Field(
        ..., description="Baseline carbon inventory to simulate against."
    )
    profile: CarbonProfile = Field(
        ..., description="User's carbon profile — needed to recompute after scenario change."
    )
    scenario: Scenario | None = Field(default=None, description="What-if scenario to evaluate.")
    scenarios: list[Scenario] = Field(
        default_factory=list, description="List of what-if scenarios to stack and evaluate."
    )


class SimulateResponse(BaseModel):
    """Response from ``POST /simulate``.

    ``delta_co2e`` is negative when emissions are reduced (the common case).
    ``years_to_break_even`` is only present when ``upfront_cost_usd`` is known.
    """

    original_total: float = Field(..., ge=0.0, description="Baseline annual total in tCO₂e.")
    new_total: float = Field(
        ..., ge=0.0, description="Projected annual total after applying the scenario."
    )
    delta_co2e: float = Field(
        ..., description="Change in annual emissions in tCO₂e (negative = reduction)."
    )
    delta_percent: float = Field(
        ..., description="Percentage change relative to baseline (negative = reduction)."
    )
    new_inventory: CarbonInventory = Field(
        ..., description="Full recalculated inventory after applying the scenario."
    )
    upfront_cost_usd: float | None = Field(
        default=None, description="Estimated one-time upfront cost in USD, if applicable."
    )
    annual_saving_usd: float | None = Field(
        default=None, description="Estimated annual cost saving in USD, if applicable."
    )
    years_to_break_even: float | None = Field(
        default=None,
        description="Years until cumulative savings offset upfront cost.",
    )
    co_benefits: list[CoBenefit] = Field(
        default_factory=list, description="Non-carbon benefits of the scenario."
    )
    applied_scenarios: list[str] = Field(
        default_factory=list, description="Names of scenarios applied (useful for AI stacking)."
    )
