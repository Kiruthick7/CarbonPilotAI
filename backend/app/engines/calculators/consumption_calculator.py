from app.models.carbon import CarbonProfile


class ConsumptionCalculator:
    @staticmethod
    def compute(profile: CarbonProfile, emission_factors: dict[str, float]) -> dict[str, float]:
        if not profile.consumption:
            return {"total": 0.0, "clothing": 0.0, "electronics": 0.0, "deliveries": 0.0}
        fc = emission_factors
        c = profile.consumption
        clothing = c.new_clothing_items_per_year * fc["clothing_per_item_kg"]
        electronics = c.new_electronics_per_year * fc["electronics_per_device_kg"]
        deliveries = c.online_deliveries_per_week * 52 * fc["delivery_per_order_kg"]
        return {"total": clothing + electronics + deliveries, "clothing": clothing, "electronics": electronics, "deliveries": deliveries}
