import { ExecutionStep } from "@/hooks/useExecutionPlan";

interface ExecutionPlanStepsProps {
  steps: ExecutionStep[];
}

export function ExecutionPlanSteps({ steps }: ExecutionPlanStepsProps) {
  return (
    <div className="mb-8">
      <h5 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
        <svg
          className="w-5 h-5 text-emerald-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
          />
        </svg>
        Step-by-Step Action Plan
      </h5>
      <div className="space-y-4">
        {steps.map((step) => (
          <div
            key={step.step_number}
            className="flex gap-4 print:break-inside-avoid"
          >
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
  );
}
