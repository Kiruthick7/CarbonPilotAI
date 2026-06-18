import React from "react";
import { MathTooltip } from "@/components/MathTooltip";
import { BeforeAfterChart } from "@/components/BeforeAfterChart";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { SimulationResult } from "@/types/simulator";
import { OcrData } from "@/context/CarbonDataContext";

interface SimulationResultsProps {
  loading: boolean;
  result: SimulationResult | null;
  activeScenario: string | null;
  data: OcrData;
}

export function SimulationResults({
  loading,
  result,
  activeScenario,
  data,
}: SimulationResultsProps) {
  return (
    <div className="bg-slate-900 text-white p-8 rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.3)] flex flex-col relative overflow-hidden ring-1 ring-white/10 lg:min-h-[600px]">
      <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/20 rounded-full blur-[100px] -mr-20 -mt-20 mix-blend-screen pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-[100px] -ml-20 -mb-20 mix-blend-screen pointer-events-none" />

      <div className="flex items-center justify-between mb-8 z-10 relative">
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-cyan-400">
          Projected Impact
        </h2>
        {activeScenario && (
          <span className="bg-white/10 px-4 py-1.5 rounded-full text-xs font-semibold text-emerald-300 backdrop-blur-md border border-white/5 shadow-sm max-w-[200px] truncate">
            {activeScenario}
          </span>
        )}
      </div>

      <div className="flex-1 bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl flex flex-col p-8 z-10 relative shadow-2xl transition-all duration-500 ease-out">
        {loading ? (
          <div
            className="flex-1 flex flex-col items-center justify-center min-h-[300px]"
            aria-live="polite"
            aria-busy="true"
          >
            <LoadingSpinner className="w-16 h-16 mb-6 text-emerald-400" />
            <p className="text-slate-300 font-medium tracking-wide animate-pulse">
              Running deterministic simulation...
            </p>
          </div>
        ) : result ? (
          <div className="animate-in fade-in zoom-in-95 duration-500 flex flex-col h-full min-h-[300px]">
            <div className="flex-1 flex flex-col items-center justify-center text-center">
              <div className="text-7xl font-black mb-2 drop-shadow-sm tracking-tighter flex items-center justify-center relative z-50">
                <MathTooltip trace={result.new_inventory?.trace}>
                  <div className="flex items-baseline bg-clip-text text-transparent bg-gradient-to-br from-emerald-300 to-emerald-600">
                    {result.delta_co2e.toFixed(2)}
                    <span className="text-3xl font-bold text-emerald-500/70 ml-2 relative -top-4">
                      tCO₂e
                    </span>
                  </div>
                </MathTooltip>
              </div>
              <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-5 py-2 rounded-full font-semibold text-sm mb-6 shadow-inner">
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
                That&apos;s a {Math.abs(result.delta_percent).toFixed(1)}%
                footprint reduction
              </div>

              {result.annual_saving_usd && result.annual_saving_usd > 0 && (
                <div className="flex items-center gap-3 bg-white/10 text-white px-6 py-3.5 rounded-2xl font-bold shadow-lg backdrop-blur-sm border border-white/10">
                  <div className="bg-emerald-500/20 p-2 rounded-full">
                    <svg
                      className="w-5 h-5 text-emerald-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  Saves approx ${Math.round(result.annual_saving_usd)} / year
                </div>
              )}
            </div>

            {result.new_inventory?.breakdowns && data.inventory.breakdowns && (
              <BeforeAfterChart
                originalBreakdowns={data.inventory.breakdowns}
                newBreakdowns={
                  result.new_inventory.breakdowns as Array<{
                    category: string;
                    total_kgco2e: number;
                  }>
                }
              />
            )}

            {result.applied_scenarios &&
              result.applied_scenarios.length > 0 && (
                <div className="w-full text-left mt-8 bg-black/20 p-4 rounded-xl border border-white/5">
                  <h4 className="text-xs uppercase tracking-widest text-emerald-400/80 font-bold mb-3 flex items-center gap-2">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                      />
                    </svg>
                    Stacked Scenarios Detected
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {result.applied_scenarios.map((sc: string, idx: number) => (
                      <span
                        key={idx}
                        className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-3 py-1.5 rounded-lg text-xs font-semibold capitalize"
                      >
                        {sc.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </div>
              )}

            {result.co_benefits && result.co_benefits.length > 0 && (
              <div className="w-full text-left mt-10 bg-black/20 p-6 rounded-2xl border border-white/5 backdrop-blur-md">
                <h4 className="text-xs uppercase tracking-widest text-emerald-400/80 font-bold mb-4 flex items-center gap-2">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
                    />
                  </svg>
                  Added Value Co-Benefits
                </h4>
                <ul className="space-y-3">
                  {result.co_benefits.map((cb, idx) => (
                    <li
                      key={idx}
                      className="text-sm text-slate-300 flex items-start gap-3"
                    >
                      <div className="mt-0.5 shrink-0 bg-emerald-500/20 p-1 rounded-md text-emerald-400">
                        <svg
                          className="w-3.5 h-3.5"
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
                      <span className="leading-relaxed">{cb.description}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-500 min-h-[300px]">
            <div className="bg-slate-800/50 p-6 rounded-full mb-6">
              <svg
                className="w-16 h-16 opacity-30 text-emerald-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
            <p className="text-lg font-medium">
              Select a scenario to calculate potential impact
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
