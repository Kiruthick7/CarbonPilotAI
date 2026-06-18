import pytest

from app.data.loader import EmissionFactorLoader
from app.models.carbon import CarbonProfile, HeatingType, HomeProfile, HomeSize
from app.services.calculator_service import CalculatorService


@pytest.mark.asyncio
async def test_home_energy_calculation_valid():
    calc = CalculatorService(loader=EmissionFactorLoader())
    profile = CarbonProfile(
        country_code="US",
        home=HomeProfile(home_size=HomeSize.MEDIUM, heating_type=HeatingType.GAS, num_occupants=2, has_solar=False, renewable_tariff=False),
        transport=None, diet=None, consumption=None
    )
    result = await calc.calculate(profile)
    assert result["inventory"].total_tco2e > 0


    categories = [b.category for b in result["inventory"].breakdowns]
    assert "home" in categories

@pytest.mark.asyncio
async def test_missing_categories_handled():
    calc = CalculatorService(loader=EmissionFactorLoader())
    profile = CarbonProfile(
        country_code="US",
        home=HomeProfile(home_size=HomeSize.MEDIUM, heating_type=HeatingType.GAS, num_occupants=2, has_solar=False, renewable_tariff=False),
        transport=None,
        diet=None,
        consumption=None
    )
    result = await calc.calculate(profile)
    [b.category for b in result["inventory"].breakdowns]


    assert next(b.total_kgco2e for b in result["inventory"].breakdowns if b.category == "diet") == 0
    assert next(b.total_kgco2e for b in result["inventory"].breakdowns if b.category == "transport") == 0
    assert next(b.total_kgco2e for b in result["inventory"].breakdowns if b.category == "consumption") == 0
