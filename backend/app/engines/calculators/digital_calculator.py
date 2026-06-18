from app.models.carbon import CarbonProfile


class DigitalCalculator:
    @staticmethod
    def compute(profile: CarbonProfile) -> dict[str, float]:
        if not profile.digital:
            return {"total": 0.0, "hardware": 0.0, "operational": 0.0}
        d = profile.digital

        # Hardware Embodied Carbon (Phone ~70kg, Laptop ~300kg)
        hw_emissions = {"frequent": 1.5, "average": 3.5, "rare": 5.0} # Lifespan in years
        lifespan = hw_emissions.get(d.device_upgrade_frequency.value, 3.5)
        hardware = (70.0 / lifespan) + (300.0 / lifespan)

        # Operational: Streaming & Gaming (0.05kg CO2e per hr)
        # Light: 0.5hr/day, Moderate: 3hr/day, Heavy: 6hr/day
        stream_hours = {"light": 0.5, "moderate": 3.0, "heavy": 6.0}
        streaming_kg = stream_hours.get(d.streaming_gaming_usage.value, 3.0) * 365 * 0.05

        # Operational: AI & Cloud Usage (LLM query ~0.005g, Image ~2g) -> Avg 0.01kg per heavy day
        ai_days = {"rare": 0.001, "occasional": 0.005, "heavy": 0.02}
        ai_kg = ai_days.get(d.ai_cloud_usage.value, 0.005) * 365

        operational = streaming_kg + ai_kg
        return {"total": hardware + operational, "hardware": hardware, "operational": operational}
