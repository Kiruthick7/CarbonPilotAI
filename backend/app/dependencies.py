"""
dependencies.py
FastAPI dependency injection wiring.
All services are constructed once (via lru_cache on the loader) and reused.
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from app.data.loader import EmissionFactorLoader
from app.services.agent_service import AgentService
from app.services.calculator_service import CalculatorService
from app.services.plan_generator_service import PlanGeneratorService
from app.services.ranker_service import RankerService
from app.services.simulator_service import SimulatorService


@lru_cache(maxsize=1)
def get_loader() -> EmissionFactorLoader:
    """Singleton data loader — JSON files read once at startup."""
    return EmissionFactorLoader()


def get_calculator(loader: EmissionFactorLoader = Depends(get_loader)) -> CalculatorService:
    """CalculatorService is stateless — safe to instantiate per-request."""
    return CalculatorService(loader)


def get_simulator(
    calculator: CalculatorService = Depends(get_calculator),
) -> SimulatorService:
    return SimulatorService(calculator)


def get_ranker(
    simulator: SimulatorService = Depends(get_simulator),
) -> RankerService:
    return RankerService(simulator)


def get_plan_generator(
    simulator: SimulatorService = Depends(get_simulator),
) -> PlanGeneratorService:
    return PlanGeneratorService(simulator)


def get_agent(
    calculator: CalculatorService = Depends(get_calculator),
    simulator: SimulatorService = Depends(get_simulator),
    ranker: RankerService = Depends(get_ranker),
) -> AgentService:
    return AgentService(calculator, simulator, ranker)
