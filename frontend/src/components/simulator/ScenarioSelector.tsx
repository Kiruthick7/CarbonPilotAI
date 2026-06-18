import React from "react";
import { SIMULATOR_SCENARIOS } from "@/constants/scenarios";

interface ScenarioSelectorProps {
  activeScenario: string | null;
  runSimulation: (params: Record<string, unknown>, name: string) => void;
  resetScenario: () => void;
}

export function ScenarioSelector({
  activeScenario,
  runSimulation,
  resetScenario,
}: ScenarioSelectorProps) {
  return (
    <>
      <div className="flex items-center gap-4 py-2">
        <div className="flex-1 h-px bg-slate-200"></div>
        <span className="text-sm font-semibold text-slate-400 uppercase tracking-widest">
          Or Pick Quick Scenario
        </span>
        <div className="flex-1 h-px bg-slate-200"></div>
      </div>

      {SIMULATOR_SCENARIOS.map((s) => (
        <button
          key={s.name}
          onClick={() => {
            if (activeScenario === s.name) {
              resetScenario();
            } else {
              runSimulation(s.params, s.name);
            }
          }}
          aria-label={`Select simulation scenario: ${s.name}`}
          aria-pressed={activeScenario === s.name}
          className={`w-full text-left p-5 rounded-2xl border-2 transition-all group relative overflow-hidden ${
            activeScenario === s.name
              ? "border-emerald-500 bg-emerald-50/50 shadow-md ring-4 ring-emerald-500/10"
              : "border-slate-200 bg-white hover:border-emerald-300 hover:shadow-lg hover:-translate-y-1"
          }`}
        >
          <div className="flex items-center gap-4 relative z-10">
            <div
              className={`p-3 rounded-xl transition-colors ${activeScenario === s.name ? "bg-white shadow-sm" : "bg-slate-50 group-hover:bg-emerald-50 group-hover:scale-110 transition-transform"}`}
            >
              {s.icon}
            </div>
            <div>
              <h3
                className={`font-bold text-lg ${activeScenario === s.name ? "text-emerald-800" : "text-slate-800 group-hover:text-emerald-700 transition-colors"}`}
              >
                {s.name}
              </h3>
              <p className="text-sm text-slate-500 mt-1">{s.subtitle}</p>
            </div>
          </div>

          {activeScenario === s.name && (
            <div className="absolute top-1/2 right-6 -translate-y-1/2 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center text-white shadow-sm animate-in zoom-in duration-300">
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={3}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          )}
        </button>
      ))}
    </>
  );
}
