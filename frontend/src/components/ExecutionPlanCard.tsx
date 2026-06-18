"use client";

import { CarbonProfile, CarbonInventory } from "@/types/carbon";
import { useExecutionPlan } from "@/hooks/useExecutionPlan";
import { ExecutionPlanHeader } from "@/components/execution-plan/ExecutionPlanHeader";
import { ExecutionPlanMetrics } from "@/components/execution-plan/ExecutionPlanMetrics";
import { ExecutionPlanSteps } from "@/components/execution-plan/ExecutionPlanSteps";
import { ExecutionPlanResources } from "@/components/execution-plan/ExecutionPlanResources";
import { SkeletonCard } from "@/components/ui/SkeletonCard";

interface ExecutionPlanCardProps {
  actionId: string;
  inventory: CarbonInventory;
  profile: CarbonProfile;
}

export default function ExecutionPlanCard({
  actionId,
  inventory,
  profile,
}: ExecutionPlanCardProps) {
  const { plan, loading, error } = useExecutionPlan(
    actionId,
    inventory,
    profile,
  );

  if (loading) {
    return <SkeletonCard />;
  }

  if (error || !plan) {
    return (
      <div className="mt-4 p-6 bg-red-50 text-red-700 rounded-xl border border-red-200">
        <p className="font-bold">Error generating plan</p>
        <p className="text-sm mt-1">{error}</p>
      </div>
    );
  }

  return (
    <div className="mt-4 p-6 bg-emerald-50/50 rounded-xl border border-emerald-100 shadow-inner">
      <ExecutionPlanHeader
        title={plan.title}
        timelineWeeks={plan.timeline_weeks}
      />

      <ExecutionPlanMetrics
        carbonSavings={plan.carbon_savings_tco2e}
        financialSavings={plan.financial_savings_usd}
        paybackPeriod={plan.payback_period_years}
      />

      <ExecutionPlanSteps steps={plan.steps} />

      <ExecutionPlanResources resources={plan.resources} />
    </div>
  );
}
