from app.models.carbon import CarbonProfile


class DigitalCalculator:
    @staticmethod
    def compute(profile: CarbonProfile) -> dict[str, float]:
        if not profile.digital:
            return {"total": 0.0, "hardware": 0.0, "operational": 0.0}
        digital = profile.digital

        hw_emissions = {"frequent": 1.5, "average": 3.5, "rare": 5.0}
        life_years = hw_emissions.get(digital.device_upgrade_frequency.value, 3.5)
        hardware = 150.0 / life_years

        stream_map = {"light": 0.5, "moderate": 3.0, "heavy": 6.0}
        stream_hrs = stream_map.get(digital.streaming_gaming_usage.value, 3.0)
        streaming_kg = stream_hrs * 365 * 0.05

        ai_map = {"rare": 0.001, "occasional": 0.005, "heavy": 0.02}
        ai_kg_val = ai_map.get(digital.ai_cloud_usage.value, 0.005)
        ai_kg = ai_kg_val * 365

        operational = streaming_kg + ai_kg
        return {"total": hardware + operational, "hardware": hardware, "operational": operational}
