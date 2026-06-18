import { useState, useEffect } from "react";
import { CarbonProfile, CarbonInventory } from "@/types/carbon";

export interface ExecutionStep {
  step_number: number;
  instruction: string;
}

export interface ExecutionResource {
  title: string;
  url: string;
}

export interface ExecutionPlan {
  action_id: string;
  title: string;
  carbon_savings_tco2e: number;
  financial_savings_usd: number;
  payback_period_years: number | null;
  timeline_weeks: string;
  steps: ExecutionStep[];
  resources: ExecutionResource[];
}

export function useExecutionPlan(
  actionId: string,
  inventory: CarbonInventory,
  profile: CarbonProfile,
) {
  const [plan, setPlan] = useState<ExecutionPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchPlan() {
      setLoading(true);
      setError(null);
      try {
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";
        const response = await fetch(`${apiUrl}/actions/generate-plan`, {
          method: "POST",
          signal: controller.signal,
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action_id: actionId,
            inventory: inventory,
            profile: profile,
          }),
        });

        if (response.ok) {
          const result = await response.json();
          setPlan(result.plan);
        } else {
          const errData = await response.json();
          setError(
            errData.detail?.message || "Failed to generate execution plan.",
          );
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") {
        } else {
          console.error("Failed to fetch plan:", err);
          setError("Network error occurred while generating the plan.");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    fetchPlan();

    return () => {
      controller.abort();
    };
  }, [actionId, inventory, profile]);

  return { plan, loading, error };
}
