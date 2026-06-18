"use client";

import { useState } from "react";
import { useCarbonData } from "@/context/CarbonDataContext";
import { useSimulation } from "@/hooks/useSimulation";
import { AiScenarioInput } from "@/components/simulator/AiScenarioInput";
import { ScenarioSelector } from "@/components/simulator/ScenarioSelector";
import { SimulationResults } from "@/components/simulator/SimulationResults";
import { LoadingState } from "@/components/ui/LoadingState";
import { EmptyState } from "@/components/ui/EmptyState";
import { SectionHeader } from "@/components/ui/SectionHeader";

export default function SimulatorPage() {
  const { ocrData: data, isHydrated } = useCarbonData();
  const [aiPrompt, setAiPrompt] = useState("");

  const {
    result,
    setResult,
    loading,
    activeScenario,
    setActiveScenario,
    isAILoading,
    runSimulation,
    runAISimulation,
  } = useSimulation(data);

  if (!isHydrated) return <LoadingState />;

  if (!data) {
    return <EmptyState message="No data found. Please complete Onboarding." />;
  }

  const resetScenario = () => {
    setActiveScenario(null);
    setResult(null);
  };

  return (
    <div>
      <SectionHeader
        title="Ask the AI"
        subtitle="Test specific lifestyle changes against your deterministic baseline to see exactly how much carbon and money you could save."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          <AiScenarioInput
            aiPrompt={aiPrompt}
            setAiPrompt={setAiPrompt}
            runAISimulation={runAISimulation}
            isAILoading={isAILoading}
          />
          <ScenarioSelector
            activeScenario={activeScenario}
            runSimulation={runSimulation}
            resetScenario={resetScenario}
          />
        </div>

        <SimulationResults
          loading={loading}
          result={result}
          activeScenario={activeScenario}
          data={data}
        />
      </div>
    </div>
  );
}
