"""Pydantic v2 models for carbon footprint profiles and inventory output.

These models are shared across the calculation engine, API routes, and the
Gemini tool-calling layer. All numeric fields carry physical-unit validation
(ge / le) so that downstream engines can trust their inputs.
"""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """Python 3.9-compatible StrEnum substitute."""
    pass
from typing import Annotated

from pydantic import BaseModel, Field


class CarType(StrEnum):
    """Fuel / propulsion type for a personal car."""

    PETROL = "petrol"
    DIESEL = "diesel"
    HYBRID = "hybrid"
    ELECTRIC = "electric"
    NONE = "none"


class DietType(StrEnum):
    """Dietary pattern, ordered from lowest to highest carbon intensity."""

    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    FLEXITARIAN = "flexitarian"
    OMNIVORE = "omnivore"
    MEAT_HEAVY = "meat_heavy"


class HeatingType(StrEnum):
    """Primary home heating fuel / system."""

    GAS = "gas"
    OIL = "oil"
    ELECTRIC = "electric"
    HEAT_PUMP = "heat_pump"
    DISTRICT = "district"


class HomeSize(StrEnum):
    """Approximate home size bracket."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class FoodWaste(StrEnum):
    """Self-reported food waste level, used as an emissions multiplier."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DeviceFrequency(StrEnum):
    """How often primary devices are upgraded."""

    FREQUENT = "frequent"
    AVERAGE = "average"
    RARE = "rare"


class DailyUsage(StrEnum):
    """Daily heavy bandwidth or screen time usage."""

    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"


class AIUsage(StrEnum):
    """Daily generative AI usage frequency."""

    RARE = "rare"
    OCCASIONAL = "occasional"
    HEAVY = "heavy"







class CarProfile(BaseModel):
    """Driving behaviour for a single car.

    ``weekly_km`` reflects average km driven per week across all trips.
    """

    car_type: CarType = Field(..., description="Fuel / propulsion type.")
    weekly_km: Annotated[float, Field(ge=0.0, le=10_000.0)] = Field(
        ..., description="Average km driven per week."
    )


class FlightProfile(BaseModel):
    """Annual flight activity.

    ``short_haul`` counts flights < 3 h; ``long_haul`` counts flights ≥ 3 h.
    Business-class multiplier is applied by the engine separately.
    """

    short_haul_flights: Annotated[int, Field(ge=0, le=365)] = Field(
        default=0, description="Number of short-haul return trips per year."
    )
    long_haul_flights: Annotated[int, Field(ge=0, le=52)] = Field(
        default=0, description="Number of long-haul return trips per year."
    )
    business_class_fraction: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        default=0.0, description="Fraction of flights taken in business class."
    )


class TransportProfile(BaseModel):
    """Combined transport behaviour."""

    car: CarProfile | None = Field(default=None, description="Car profile, or None if car-free.")
    flights: FlightProfile = Field(
        default_factory=FlightProfile,
        description="Annual flight activity.",
    )
    weekly_public_transport_km: Annotated[float, Field(ge=0.0, le=5_000.0)] = Field(
        default=0.0, description="Weekly km on bus and/or train combined."
    )
    public_transport_split_bus: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        default=0.5,
        description="Fraction of public transport km taken by bus (remainder = train).",
    )


class DietProfile(BaseModel):
    """Dietary habits and food-waste behaviour."""

    diet_type: DietType = Field(..., description="Primary dietary pattern.")
    food_waste: FoodWaste = Field(
        default=FoodWaste.MEDIUM, description="Self-reported food waste level."
    )
    locally_sourced_fraction: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        default=0.0,
        description="Fraction of food that is locally / seasonally sourced (0-1).",
    )


class HomeProfile(BaseModel):
    """Home energy consumption and characteristics."""

    home_size: HomeSize = Field(..., description="Approximate size bracket.")
    heating_type: HeatingType = Field(..., description="Primary heating fuel/system.")
    num_occupants: Annotated[int, Field(ge=1, le=20)] = Field(
        default=2, description="Number of people sharing the home's energy bills."
    )
    has_solar: bool = Field(
        default=False, description="Whether the home has rooftop solar panels."
    )
    renewable_tariff: bool = Field(
        default=False,
        description="Whether the household is on a 100 % renewable electricity tariff.",
    )


class ConsumptionProfile(BaseModel):
    """Discretionary spending and consumption behaviour."""

    new_clothing_items_per_year: Annotated[int, Field(ge=0, le=500)] = Field(
        default=20, description="Number of new clothing items bought per year."
    )
    new_electronics_per_year: Annotated[int, Field(ge=0, le=50)] = Field(
        default=2, description="Number of new electronic devices bought per year."
    )
    online_deliveries_per_week: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        default=3.0, description="Average online delivery parcels received per week."
    )


class DigitalProfile(BaseModel):
    """Digital lifestyle and tech consumption behaviour."""

    device_upgrade_frequency: DeviceFrequency = Field(
        ..., description="How often you replace your primary devices."
    )
    streaming_gaming_usage: DailyUsage = Field(
        ..., description="Daily heavy bandwidth usage (Netflix, Gaming)."
    )
    ai_cloud_usage: AIUsage = Field(
        ..., description="Daily generative AI & heavy cloud computing usage."
    )







class CarbonProfile(BaseModel):
    """Complete user carbon profile.

    All sub-profiles are required; ``country_code`` drives grid intensity and
    national-average comparisons.
    """

    country_code: str = Field(
        ...,
        min_length=2,
        max_length=2,
        pattern=r"^[A-Z]{2}$",
        description="ISO 3166-1 alpha-2 country code (upper-case).",
    )
    transport: TransportProfile | None = Field(default=None, description="Transport behaviour.")
    diet: DietProfile | None = Field(default=None, description="Dietary habits.")
    home: HomeProfile = Field(..., description="Home energy profile.")
    consumption: ConsumptionProfile | None = Field(
        default=None,
        description="Discretionary consumption profile.",
    )
    digital: DigitalProfile | None = Field(
        default=None,
        description="Digital lifestyle and tech footprint.",
    )







class CarbonProfilePartial(BaseModel):
    """Partially-known carbon profile built up during chat onboarding.

    Every field is optional so the model can be constructed incrementally.
    """

    country_code: str | None = Field(default=None, description="ISO 3166-1 alpha-2 country code.")
    transport: TransportProfile | None = Field(default=None)
    diet: DietProfile | None = Field(default=None)
    home: HomeProfile | None = Field(default=None)
    consumption: ConsumptionProfile | None = Field(default=None)
    digital: DigitalProfile | None = Field(default=None)







class SubcategoryItem(BaseModel):
    """A single sub-category line-item within a category breakdown."""

    label: str = Field(..., description="Human-readable sub-category name.")
    kgco2e: float = Field(..., ge=0.0, description="Emissions in kg CO₂e.")
    share_of_category: float = Field(
        ..., ge=0.0, le=1.0, description="Fraction of the parent category total."
    )


class CategoryBreakdown(BaseModel):
    """Emissions for one top-level category with itemised sub-breakdown."""

    category: str = Field(..., description="Category name, e.g. 'transport'.")
    total_kgco2e: float = Field(..., ge=0.0, description="Total kg CO₂e for this category.")
    subcategories: list[SubcategoryItem] = Field(
        default_factory=list, description="Itemised sub-breakdown."
    )


class CalculationTrace(BaseModel):
    """Transparency trace proving deterministic calculation."""

    formula: str = Field(..., description="The mathematical formula used.")
    variables: dict[str, str] = Field(..., description="The exact values plugged into the formula.")
    source: str = Field(..., description="The source or citation for the emission factor.")


class CarbonInventory(BaseModel):
    """Full calculated carbon inventory for a user profile.

    ``total_tco2e`` is the authoritative annual total in metric tonnes.
    ``breakdowns`` contains one entry per top-level category.
    """

    total_tco2e: float = Field(..., ge=0.0, description="Annual total in tCO₂e.")
    breakdowns: list[CategoryBreakdown] = Field(
        default_factory=list, description="Per-category breakdowns."
    )
    national_average_tco2e: float | None = Field(
        default=None, description="National per-person average in tCO₂e (for comparison)."
    )
    global_average_tco2e: float = Field(
        default=4.8, description="Global per-person average in tCO₂e (for comparison)."
    )
    budget_1_5c_tco2e: float = Field(
        default=2.3, description="IPCC 1.5°C annual per-person carbon budget in tCO₂e."
    )
    trace: CalculationTrace | None = Field(
        default=None, description="Transparency trace proving deterministic calculation."
    )
