from typing import Any

from app.models.carbon import (
    CarbonInventory,
    CarbonProfile,
    CategoryBreakdown,
    HeatingType,
    HomeProfile,
    HomeSize,
    SubcategoryItem,
)
from app.services.calculator_service import CalculatorService


async def build_inventory_for_data(
    calculator: CalculatorService, kwh: float, parsed: dict[str, Any]
) -> tuple[CarbonProfile, CarbonInventory, float]:
    profile = CarbonProfile(
        country_code="US",
        transport=None,
        diet=None,
        home=HomeProfile(
            home_size=HomeSize.MEDIUM,
            heating_type=HeatingType.GAS,
            num_occupants=2,
            has_solar=False,
            renewable_tariff=False,
        ),
        consumption=None,
    )

    calc_result = await calculator.calculate(profile)
    inventory = calc_result["inventory"]

    footprint_kg = kwh * 0.385
    footprint_tco2e = round(footprint_kg / 1000.0, 3)

    new_total_tco2e = 0.0

    existing_cats = set()
    for breakdown in inventory.breakdowns:
        cat = breakdown.category
        existing_cats.add(cat)

        if cat in parsed:
            val_tco2e = parsed[cat]
            val_kg = val_tco2e * 1000.0

            breakdown.total_kgco2e = val_kg
            if cat == "home":
                for sub in breakdown.subcategories:
                    if sub.label.lower() == "electricity":
                        sub.kgco2e = val_kg
                        sub.share_of_category = 1.0
                    else:
                        sub.kgco2e = 0.0
                        sub.share_of_category = 0.0
            else:
                if breakdown.subcategories:
                    breakdown.subcategories[0].kgco2e = val_kg
                    breakdown.subcategories[0].share_of_category = 1.0
                    for sub in breakdown.subcategories[1:]:
                        sub.kgco2e = 0.0
                        sub.share_of_category = 0.0

            new_total_tco2e += val_tco2e

        elif cat == "home" and "home" not in parsed and kwh > 0:
            breakdown.total_kgco2e = footprint_kg
            for sub in breakdown.subcategories:
                if sub.label.lower() == "electricity":
                    sub.kgco2e = footprint_kg
                    sub.share_of_category = 1.0
                else:
                    sub.kgco2e = 0.0
                    sub.share_of_category = 0.0
            new_total_tco2e += footprint_tco2e

    for parsed_cat, parsed_tco2e in parsed.items():
        if parsed_cat not in existing_cats:
            val_kg = parsed_tco2e * 1000.0
            new_breakdown = CategoryBreakdown(
                category=parsed_cat,
                total_kgco2e=val_kg,
                subcategories=[
                    SubcategoryItem(
                        label="Extracted from Bill", kgco2e=val_kg, share_of_category=1.0
                    )
                ],
            )
            inventory.breakdowns.append(new_breakdown)
            new_total_tco2e += parsed_tco2e

    inventory.total_tco2e = round(new_total_tco2e, 3)
    return profile, inventory, footprint_tco2e
