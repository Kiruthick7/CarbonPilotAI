"""
models/actions.py
Pydantic v2 models for the action-ranking endpoint.
Python 3.9 compatible — uses str+Enum mixin instead of StrEnum.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from app.models.carbon import CarbonInventory
from app.models.simulation import CoBenefit


class StrEnum(str, Enum):
    """Python 3.9-compatible StrEnum substitute."""
    pass


class ActionCategory(StrEnum):
    """Top-level category grouping for recommended actions."""
    TRANSPORT   = "transport"
    DIET        = "diet"
    HOME        = "home"
    CONSUMPTION = "consumption"
    DIGITAL     = "digital"


class UserConstraints(BaseModel):
    """Optional lifestyle and financial constraints that filter actions."""

    max_upfront_cost_usd: float | None = Field(
        default=None,
        description="Maximum one-time investment the user is willing to make (USD).",
    )
    exclude_categories: list[str] = Field(
        default_factory=list,
        description="Category names the user wishes to exclude.",
    )
    lifestyle_flags: dict[str, bool] = Field(
        default_factory=dict,
        description="Free-form lifestyle constraints, e.g. {'rents_home': true}.",
    )


class RankActionsRequest(BaseModel):
    """Request body for POST /actions/rank."""
    inventory: CarbonInventory = Field(..., description="User's current carbon inventory.")
    constraints: UserConstraints = Field(
        default_factory=UserConstraints,
        description="Optional lifestyle and budget constraints.",
    )


class RankedAction(BaseModel):
    """A single recommended action with impact, effort, and cost estimates."""

    id: str = Field(..., description="Stable slug identifier.")
    title: str = Field(..., description="Short action title.")
    description: str = Field(..., description="Full explanation of the action.")
    category: ActionCategory = Field(..., description="Top-level category.")
    co2e_saved_per_year: float = Field(..., ge=0.0, description="Annual CO₂e saving in tCO₂e.")
    effort_score: Annotated[int, Field(ge=1, le=5)] = Field(..., description="Effort: 1 (easy) - 5 (major change).")
    impact_score: Annotated[int, Field(ge=1, le=5)] = Field(..., description="Impact: 1 (negligible) - 5 (transformational).")
    composite_score: float = Field(..., ge=0.0, description="Weighted ranking score (higher = better).")
    upfront_cost_usd: float = Field(default=0.0, ge=0.0, description="Estimated upfront cost in USD.")
    annual_saving_usd: float = Field(default=0.0, ge=0.0, description="Estimated annual monetary saving in USD.")
    time_to_impact_days: Annotated[int, Field(ge=0, le=3650)] = Field(default=0, description="Days until saving is realised.")
    co_benefits: list[CoBenefit] = Field(default_factory=list, description="Non-carbon positive side-effects.")
    why_recommended: str = Field(..., description="Explanation of why this action was recommended based on verified data.")
    is_feasible: bool = Field(default=True, description="Whether this action is feasible given constraints.")
    feasibility_reason: str | None = Field(default=None, description="Explanation when is_feasible is False.")


class RankActionsResponse(BaseModel):
    """Response from POST /actions/rank."""
    actions: list[RankedAction] = Field(default_factory=list, description="Ranked actions, best first.")
    total_achievable_reduction: float = Field(..., ge=0.0, description="Sum of feasible annual CO₂e savings in tCO₂e.")


class ExecutionStep(BaseModel):
    step_number: int = Field(..., description="Order of the step.")
    instruction: str = Field(..., description="Actionable instruction.")


class ExecutionResource(BaseModel):
    title: str = Field(..., description="Title of the resource.")
    url: str = Field(..., description="URL to external resource.")


class ExecutionPlan(BaseModel):
    """A 5-part execution plan bridging the gap between diagnosis and execution."""
    action_id: str = Field(..., description="The ID of the action.")
    title: str = Field(..., description="The title of the action.")
    carbon_savings_tco2e: float = Field(..., description="Annual carbon savings.")
    financial_savings_usd: float = Field(..., description="Annual financial savings.")
    payback_period_years: float | None = Field(default=None, description="Payback period if applicable.")
    timeline_weeks: str = Field(..., description="Expected implementation timeline.")
    steps: list[ExecutionStep] = Field(..., description="Step-by-step action plan.")
    resources: list[ExecutionResource] = Field(..., description="External resources.")


class PlanGenerationRequest(BaseModel):
    """Request body for POST /actions/generate-plan."""
    action_id: str = Field(..., description="The ID of the action to generate a plan for.")
    inventory: CarbonInventory = Field(..., description="User's current carbon inventory.")
    profile: dict = Field(..., description="User's carbon profile dict.")


class ExecutionPlanResponse(BaseModel):
    """Response from POST /actions/generate-plan."""
    plan: ExecutionPlan = Field(..., description="The generated execution plan.")
