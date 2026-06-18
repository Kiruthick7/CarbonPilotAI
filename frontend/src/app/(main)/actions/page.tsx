"use client";

import { useCarbonData } from "@/context/CarbonDataContext";
import { LoadingState } from "@/components/ui/LoadingState";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { ActionFilters } from "@/components/actions/ActionFilters";
import { ActionList } from "@/components/actions/ActionList";

export default function ActionsPage() {
  const {
    ocrData,
    isHydrated,
    actions,
    loadingActions: loading,
    actionsView: activeView,
    setActionsView: setActiveView,
  } = useCarbonData();

  if (!isHydrated) return <LoadingState />;

  return (
    <div>
      <div className="flex flex-col md:flex-row items-start justify-between mb-6 gap-4">
        <div>
          <h1 className="text-3xl font-bold">Action Plan</h1>
          <p className="text-gray-500 mt-2 max-w-2xl">
            Personalized climate actions sorted by their potential impact and
            feasibility based on your deterministic profile.
          </p>
        </div>

        <ActionFilters
          ocrData={ocrData}
          activeView={activeView}
          setActiveView={setActiveView}
        />
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <LoadingSpinner className="h-8 w-8 text-emerald-500" />
        </div>
      ) : actions.length === 0 ? (
        <EmptyState message="No actions available. Please complete onboarding." />
      ) : (
        <ActionList
          actions={actions}
          ocrData={ocrData}
          activeView={activeView}
        />
      )}
    </div>
  );
}
