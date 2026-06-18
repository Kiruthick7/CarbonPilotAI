from collections.abc import Callable
from typing import Any

from app.models.actions import ActionCategory, UserConstraints
from app.models.carbon import CarbonInventory


class ActionTemplate:
    """Static definition of a possible action."""

    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        category: ActionCategory,
        scenario_type: str,
        scenario_params: dict[str, Any],
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
