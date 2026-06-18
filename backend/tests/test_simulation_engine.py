import pytest

from app.engines.simulation_engine import SimulationEngine
from app.models.carbon import (
    CarbonInventory,
    CarbonProfile,
    CarType,
    HeatingType,
    HomeProfile,
    HomeSize,
    TransportProfile,
)
from app.models.simulation import SwitchCarParams, SwitchHeatingParams


@pytest.fixture
def base_profile():
    return CarbonProfile(
        country_code="US",
        home=HomeProfile(home_size=HomeSize.MEDIUM, heating_type=HeatingType.GAS, num_occupants=2, has_solar=False, renewable_tariff=False),
        transport=TransportProfile(car={"car_type": CarType.PETROL, "weekly_km": 300})
    )

@pytest.fixture
def base_inventory():
    return CarbonInventory(total_tco2e=12.5, breakdowns=[])

def test_single_scenario_apply(base_profile):
    engine = SimulationEngine()
    scenario = SwitchCarParams(new_car_type=CarType.ELECTRIC)
    modified = engine.apply_scenario(base_profile, scenario)
    assert modified.transport.car.car_type == CarType.ELECTRIC

def test_stacked_scenarios_apply(base_profile):
    engine = SimulationEngine()
    s1 = SwitchCarParams(new_car_type=CarType.ELECTRIC)
    s2 = SwitchHeatingParams(new_heating_type=HeatingType.HEAT_PUMP)

    mod1 = engine.apply_scenario(base_profile, s1)
    mod2 = engine.apply_scenario(mod1, s2)

    assert mod2.transport.car.car_type == CarType.ELECTRIC
    assert mod2.home.heating_type == HeatingType.HEAT_PUMP

def test_compute_delta_stacked(base_inventory):
    engine = SimulationEngine()
    new_inventory = CarbonInventory(total_tco2e=8.0, breakdowns=[])

    s1 = SwitchCarParams(new_car_type=CarType.ELECTRIC)
    s2 = SwitchHeatingParams(new_heating_type=HeatingType.HEAT_PUMP)

    result = engine.compute_delta(base_inventory, new_inventory, scenarios=[s1, s2])

    assert result.delta_co2e == -4.5
    assert result.delta_percent == -36.0
    assert result.upfront_cost_usd == 20000.0
    assert result.annual_saving_usd == 2200.0
    assert result.years_to_break_even == round(20000.0 / 2200.0, 1)
