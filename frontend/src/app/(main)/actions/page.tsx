"use client";

import { useState } from "react";
import ExecutionPlanCard from "@/components/ExecutionPlanCard";

import { useCarbonData, type RankedAction } from "@/context/CarbonDataContext";

export default function ActionsPage() {
  const { ocrData, isHydrated, actions, loadingActions: loading, actionsView: activeView, setActionsView: setActiveView } = useCarbonData();
  const [committedActions, setCommittedActions] = useState<string[]>([]);

  if (!isHydrated) {
    return (
      <div className="flex justify-center py-10">
        <svg className="animate-spin h-8 w-8 text-emerald-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col md:flex-row items-start justify-between mb-6 gap-4">
        <div>
          <h1 className="text-3xl font-bold">Action Plan</h1>
          <p className="text-gray-500 mt-2 max-w-2xl">Personalized climate actions sorted by their potential impact and feasibility based on your deterministic profile.</p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0 w-full md:w-auto md:ml-4">
          {ocrData?.individual_results && ocrData.individual_results.length > 1 && (
            <select
              value={activeView}
              onChange={(e) => setActiveView(e.target.value === "combined" ? "combined" : parseInt(e.target.value))}
              className="bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 font-medium shadow-sm outline-none print:hidden"
            >
              <option value="combined">Combined View (All Files)</option>
              {ocrData.individual_results.map((result, idx: number) => (
                <option key={idx} value={idx}>File: {result.filename}</option>
              ))}
            </select>
          )}
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 bg-slate-900 text-white px-4 py-2.5 rounded-lg text-sm font-semibold shadow-sm hover:bg-slate-800 transition print:hidden"
            aria-label="Export Action Plan as PDF"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export PDF
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <svg className="animate-spin h-8 w-8 text-emerald-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      ) : actions.length === 0 ? (
        <div className="bg-gray-50 border border-dashed rounded-xl p-8 text-center text-gray-500">
          No actions available. Please complete onboarding.
        </div>
      ) : (
        <div className="space-y-8">
          {(() => {
            const highImpact = actions.filter(a => Math.abs(a.co2e_saved_per_year) >= 1.0);
            const quickWins = actions.filter(a => Math.abs(a.co2e_saved_per_year) < 1.0);

            const renderActionGroup = (title: string, groupActions: RankedAction[], icon: React.ReactNode) => (
              groupActions.length > 0 && (
                <div className="mb-8">
                  <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                    {icon}
                    {title}
                  </h2>
                  <div className="space-y-4">
                    {groupActions.map((action, i) => {
                      const isCommitted = committedActions.includes(action.id);
                      return (
                        <div key={action.id} className="flex flex-col">
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col md:flex-row justify-between items-start md:items-center transition hover:shadow-md hover:border-emerald-200 z-10 relative">
                          <div className="flex items-start gap-4 mb-4 md:mb-0">
                            <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 font-bold shrink-0 mt-1">
                              #{i + 1}
                            </div>
                            <div>
                              <h3 className="text-lg font-bold text-gray-900">{action.title}</h3>
                              <p className="text-gray-600 text-sm mt-1">{action.description}</p>
                              <div className="mt-3 bg-slate-50 border border-slate-100 rounded-lg p-3 text-sm text-slate-700 flex gap-2 items-start">
                                <svg className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                <p>{action.why_recommended}</p>
                              </div>
                              <p className="text-emerald-700 font-bold text-sm mt-3">Potential savings: {Math.abs(action.co2e_saved_per_year).toFixed(2)} tCO₂e / yr</p>
                              <div className="mt-3 flex flex-wrap gap-2">
                                <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded text-xs font-medium capitalize">Effort: {action.effort_score}/5</span>
                                <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded text-xs font-medium capitalize">Category: {action.category}</span>
                                {action.annual_saving_usd ? (
                                   <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-bold">Saves ${Math.round(action.annual_saving_usd)}/yr</span>
                                ) : null}
                              </div>
                            </div>
                          </div>
                          <div className="flex flex-col gap-2 w-full md:w-auto shrink-0 md:ml-4">
                            <button
                              onClick={() => {
                                if (isCommitted) {
                                  setCommittedActions(prev => prev.filter(id => id !== action.id));
                                } else {
                                  setCommittedActions(prev => [...prev, action.id]);
                                }
                              }}
                              className={`w-full md:w-auto px-5 py-3 rounded-xl font-bold shadow-sm transition ${
                                isCommitted
                                  ? "bg-slate-100 text-slate-600 border border-slate-300 hover:bg-slate-200"
                                  : "bg-emerald-600 text-white hover:bg-emerald-700 hover:shadow-md active:transform active:scale-95"
                              }`}
                            >
                              {isCommitted ? "Hide Execution Plan" : "Generate Execution Plan"}
                            </button>
                            {!isCommitted && (
                               <p className="text-[10px] text-center text-slate-400 mt-1 uppercase tracking-wider font-semibold">AI Agent Action</p>
                            )}
                          </div>
                        </div>
                        {isCommitted && ocrData && (
                          <div className="mt-[-8px]">
                            <ExecutionPlanCard
                              actionId={action.id}
                              inventory={activeView === "combined" ? ocrData.inventory : (ocrData.individual_results?.[activeView as number]?.inventory || ocrData.inventory)}
                              profile={activeView === "combined" ? ocrData.profile : (ocrData.individual_results?.[activeView as number]?.profile || ocrData.profile)}
                            />
                          </div>
                        )}
                      </div>
                    );
                    })}
                  </div>
                </div>
              )
            );

            return (
              <>
                {renderActionGroup(
                  "High Impact Interventions",
                  highImpact,
                  <svg className="w-6 h-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                )}
                {renderActionGroup(
                  "Quick Wins",
                  quickWins,
                  <svg className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                )}
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
}
