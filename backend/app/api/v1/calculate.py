"""
api/v1/calculate.py
POST /v1/calculate — deterministic carbon footprint calculation.
No AI involved. Always fast. The source of truth for all numbers.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_calculator
from app.models.carbon import CarbonProfile
from app.models.errors import ErrorCode, ErrorResponse
from app.services.calculator_service import CalculatorService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post(
    "/calculate",
    summary="Calculate carbon footprint",
    response_description="Full carbon inventory with category breakdowns and peer comparison",
)
async def calculate_footprint(
    profile: CarbonProfile,
    calculator: CalculatorService = Depends(get_calculator),
) -> dict:
    """
    Deterministic carbon footprint calculation.
    Uses IPCC AR6 / IEA 2023 / DEFRA 2023 emission factors.
    Returns the full CarbonInventory with subcategory breakdowns,
    national peer comparison, and 1.5°C budget context.
    """
    try:
        result = await calculator.calculate(profile)
        return {
            "inventory": result["inventory"].model_dump(),
            "calculation_version": result["calculation_version"],
            "factors_used": result["factors_used"],
        }
    except ValueError as e:
        logger.warning("calculate_validation_error", error=str(e))
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                code=ErrorCode.INVALID_PROFILE,
                message=str(e),
            ).model_dump(),
        )
    except Exception as e:
        logger.error("calculate_internal_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                code=ErrorCode.CALCULATION_ERROR,
                message="Calculation failed. Please try again.",
            ).model_dump(),
        )
