"use client";

import { useMemo } from "react";

import { useCarbonData } from "@/context/CarbonDataContext";
import { LoadingState } from "@/components/ui/LoadingState";
import { EmptyState } from "@/components/ui/EmptyState";
import { DashboardSummary } from "@/components/dashboard/DashboardSummary";
import { DashboardMetrics } from "@/components/dashboard/DashboardMetrics";
import { DashboardInsights } from "@/components/dashboard/DashboardInsights";

export default function DashboardPage() {
  const {
    ocrData,
    isHydrated,
    actionsView: activeView,
    setActionsView: setActiveView,
  } = useCarbonData();

  const currentData = useMemo(() => {
    if (!ocrData) return null;
    if (activeView === "combined") return ocrData;
    if (typeof activeView === "number" && ocrData.individual_results) {
      return ocrData.individual_results[activeView] ?? ocrData;
    }
    return ocrData;
  }, [activeView, ocrData]);

  const totalKg = useMemo(() => {
    if (!currentData) return 0;
    return (currentData.inventory?.total_tco2e || 0) * 1000;
  }, [currentData]);

  if (!isHydrated) return <LoadingState />;

  if (!ocrData || !currentData) {
    return (
      <EmptyState message="No data found. Please complete the Onboarding step." />
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        {ocrData.individual_results &&
          ocrData.individual_results.length > 1 && (
            <select
              id="dashboard-view-select"
              name="dashboard-view-select"
              value={activeView}
              onChange={(e) =>
                setActiveView(
                  e.target.value === "combined"
                    ? "combined"
                    : parseInt(e.target.value),
                )
              }
              className="bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 font-medium shadow-sm outline-none"
              aria-label="Select data view"
            >
              <option value="combined">Combined View (All Files)</option>
              {ocrData.individual_results.map((result, idx) => (
                <option key={idx} value={idx}>
                  File: {result.filename}
                </option>
              ))}
            </select>
          )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <DashboardSummary currentData={currentData} />
        <DashboardMetrics currentData={currentData} />
      </div>

      <DashboardInsights currentData={currentData} totalKg={totalKg} />
    </div>
  );
}
