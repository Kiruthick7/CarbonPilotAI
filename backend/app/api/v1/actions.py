from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_plan_generator, get_ranker
from app.models.actions import (
    ExecutionPlanResponse,
    PlanGenerationRequest,
    RankActionsRequest,
    RankActionsResponse,
)
from app.models.carbon import CarbonProfile
from app.models.errors import ErrorCode, ErrorResponse
from app.services.plan_generator_service import PlanGeneratorService
from app.services.ranker_service import RankerService

logger = structlog.get_logger(__name__)
router = APIRouter()


class RankRequest(RankActionsRequest):
    profile: CarbonProfile


@router.post(
    "/actions/rank",
    response_model=RankActionsResponse,
    summary="Generate ranked action plan",
)
async def rank_actions(
    request: RankRequest,
    ranker: RankerService = Depends(get_ranker),
) -> RankActionsResponse:
    try:
        return await ranker.rank(request, request.profile)
    except Exception as e:
        logger.error("rank_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                code=ErrorCode.SYS_INTERNAL_ERROR,
                message="Action ranking failed.",
            ).model_dump(),
        )


@router.post(
    "/actions/generate-plan",
    response_model=ExecutionPlanResponse,
    summary="Generate a step-by-step execution plan",
)
async def generate_plan(
    request: PlanGenerationRequest,
    plan_generator: PlanGeneratorService = Depends(get_plan_generator),
) -> ExecutionPlanResponse:
    try:
        return await plan_generator.generate_plan(request)
    except ValueError as e:
        logger.warning("generate_plan_invalid_action", error=str(e))
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                code=ErrorCode.VAL_INVALID_REQUEST,
                message=str(e),
            ).model_dump(),
        )
    except Exception as e:
        logger.error("generate_plan_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                code=ErrorCode.SYS_INTERNAL_ERROR,
                message="Execution plan generation failed.",
            ).model_dump(),
        )
