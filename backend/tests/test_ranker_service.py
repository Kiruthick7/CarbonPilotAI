import asyncio

from app.models.actions import RankActionsRequest
from app.models.carbon import (
    CarbonInventory,
    CarbonProfile,
    CarType,
    HeatingType,
    HomeProfile,
    HomeSize,
    TransportProfile,
)
from app.services.ranker_service import RankerService


def test_ranker_filters_contextually():
    profile = CarbonProfile(
        country_code="US",
        home=HomeProfile(home_size=HomeSize.MEDIUM, heating_type=HeatingType.HEAT_PUMP, num_occupants=2, has_solar=True, renewable_tariff=True),
        transport=TransportProfile(car={"car_type": CarType.ELECTRIC, "weekly_km": 200})
    )

    class MockSimulator:
        async def simulate_for_template(self, inv, prof, stype, params):
            from app.models.carbon import CarbonInventory
            from app.models.simulation import SimulateResponse
            return SimulateResponse(
                original_total=10.0,
                new_total=8.0,
                delta_co2e=-2.0,
                delta_percent=-20.0,
                new_inventory=CarbonInventory(total_tco2e=8.0, breakdowns=[]),
                co_benefits=[],
                applied_scenarios=[]
            )

    ranker = RankerService(simulator=MockSimulator())


    request = RankActionsRequest(inventory=CarbonInventory(total_tco2e=10.0, breakdowns=[]))
    response = asyncio.run(ranker.rank(request, profile))
    rankings = response.actions


    recommended_types = [r.action_id for r in rankings]
    assert "switch_car" not in recommended_types
    assert "switch_heating" not in recommended_types
