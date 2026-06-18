"""
calculator_service.py — aligned to existing carbon model field names.
"""

from __future__ import annotations

import structlog

from app.data.loader import EmissionFactorLoader
from app.engines.carbon_engine import CarbonEngine, EmissionFactors
from app.models.carbon import CarbonInventory, CarbonProfile

logger = structlog.get_logger(__name__)


class CalculatorService:
    """
    Service layer between the API router and the CarbonEngine.
    Stateless after construction — safe to share across requests.
    """

    def __init__(self, loader: EmissionFactorLoader) -> None:
        factors = EmissionFactors(
            transport=loader.factors["transport"],
            diet=loader.factors["diet"],
            food_waste_multipliers=loader.factors["food_waste_multipliers"],
            home=loader.factors["home"],
            consumption=loader.factors["consumption"],
            version=loader.factors["version"],
            grid_intensity=loader.grid_intensity,
            benchmarks=loader.benchmarks,
        )
        self._engine = CarbonEngine(factors=factors)
        logger.info("calculator_service_ready", version=factors.version)

    @property
    def engine(self) -> CarbonEngine:
        return self._engine

    async def calculate(self, profile: CarbonProfile) -> dict:
        """Compute inventory and return as dict with metadata."""
        logger.info(
            "calculating_footprint",
            country=profile.country_code,
            diet=profile.diet.diet_type.value if profile.diet else "unknown",
        )
        inventory: CarbonInventory = self._engine.compute(profile)
        factors_used = self._engine.get_factors_used(profile)
        percentile = self._engine.compute_percentile(
            inventory.total_tco2e,
            inventory.national_average_tco2e or 4.8,
        )
        logger.info(
            "calculation_complete",
            total_tco2e=inventory.total_tco2e,
            percentile=percentile,
        )
        return {
            "inventory": inventory,
            "calculation_version": self._engine.version,
            "factors_used": factors_used,
            "percentile_vs_national": percentile,
        }
