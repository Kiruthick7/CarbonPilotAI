"use client";

import { useEffect, useState } from "react";

interface ExecutionStep {
  step_number: number;
  instruction: string;
}

interface ExecutionResource {
  title: string;
  url: string;
}

interface ExecutionPlan {
  action_id: string;
  title: string;
  carbon_savings_tco2e: number;
  financial_savings_usd: number;
  payback_period_years: number | null;
  timeline_weeks: string;
  steps: ExecutionStep[];
  resources: ExecutionResource[];
}

interface ExecutionPlanCardProps {
  actionId: string;
  inventory: Record<string, unknown>;
  profile: Record<string, unknown>;
}

export default function ExecutionPlanCard({ actionId, inventory, profile }: ExecutionPlanCardProps) {
  const [plan, setPlan] = useState<ExecutionPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchPlan() {
      setLoading(true);
      setError(null);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";
        const response = await fetch(`${apiUrl}/actions/generate-plan`, {
          method: "POST",
          signal: controller.signal,
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            action_id: actionId,
            inventory: inventory,
            profile: profile
          })
        });

        if (response.ok) {
          const result = await response.json();
          setPlan(result.plan);
        } else {
          const errData = await response.json();
          setError(errData.detail?.message || "Failed to generate execution plan.");
        }
      } catch (err: unknown) {
        if ((err as Error).name === 'AbortError') {
          console.log("Fetch aborted");
          return;
        }
        console.error("Failed to fetch plan:", err);
        setError("Network error occurred while generating the plan.");
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

  if (loading) {
    return (
      <div className="mt-4 p-6 bg-slate-50 rounded-xl border border-slate-200 animate-pulse">
        <div className="h-6 bg-slate-200 rounded w-1/3 mb-4"></div>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="h-20 bg-slate-200 rounded-lg"></div>
          <div className="h-20 bg-slate-200 rounded-lg"></div>
          <div className="h-20 bg-slate-200 rounded-lg"></div>
        </div>
        <div className="space-y-3">
          <div className="h-4 bg-slate-200 rounded w-3/4"></div>
          <div className="h-4 bg-slate-200 rounded w-2/3"></div>
          <div className="h-4 bg-slate-200 rounded w-5/6"></div>
        </div>
      </div>
    );
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
      <div className="flex items-center justify-between mb-6">
        <h4 className="text-lg font-bold text-slate-900">Execution Plan: {plan.title}</h4>
        <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
          Timeline: {plan.timeline_weeks}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm text-center">
          <p className="text-sm text-slate-500 font-semibold mb-1 uppercase tracking-wider">Carbon Impact</p>
          <p className="text-2xl font-bold text-emerald-600">↓ {plan.carbon_savings_tco2e} <span className="text-sm font-medium">tCO₂e/yr</span></p>
        </div>
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm text-center">
          <p className="text-sm text-slate-500 font-semibold mb-1 uppercase tracking-wider">Financial ROI</p>
          <p className="text-2xl font-bold text-green-600">
            {plan.financial_savings_usd > 0 ? `+$${plan.financial_savings_usd}` : "N/A"} <span className="text-sm font-medium">/yr</span>
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm text-center">
          <p className="text-sm text-slate-500 font-semibold mb-1 uppercase tracking-wider">Payback Period</p>
          <p className="text-2xl font-bold text-blue-600">
            {plan.payback_period_years !== null ? `${plan.payback_period_years} yrs` : "Immediate"}
          </p>
        </div>
      </div>

      <div className="mb-8">
        <h5 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
          Step-by-Step Action Plan
        </h5>
        <div className="space-y-4">
          {plan.steps.map((step) => (
            <div key={step.step_number} className="flex gap-4 print:break-inside-avoid">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold shadow-sm">
                {step.step_number}
              </div>
              <div className="bg-white flex-grow p-4 rounded-lg border border-slate-200 shadow-sm">
                <p className="text-slate-800 font-medium">{step.instruction}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {plan.resources.length > 0 && (
        <div>
          <h5 className="font-bold text-slate-900 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
            Helpful Resources & Links
          </h5>
          <div className="flex flex-wrap gap-3">
            {plan.resources.map((resource, i) => (
              <a 
                key={i} 
                href={resource.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition shadow-sm"
              >
                {resource.title}
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
