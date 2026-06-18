import { useState } from "react";
import { OcrData } from "@/context/CarbonDataContext";
import { SimulationResult } from "@/types/simulator";

export function useSimulation(data: OcrData | null) {
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [isAILoading, setIsAILoading] = useState(false);

  const runSimulation = async (
    scenarioParams: Record<string, unknown>,
    name: string,
  ) => {
    if (!data || !data.inventory || !data.profile) return;
    setLoading(true);
    setActiveScenario(name);
    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";
      const response = await fetch(`${apiUrl}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          inventory: data.inventory,
          profile: data.profile,
          scenario: scenarioParams,
        }),
      });
      if (response.ok) {
        setResult(await response.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runAISimulation = async (aiPrompt: string) => {
    if (!data || !data.inventory || !data.profile || !aiPrompt.trim()) return;
    setIsAILoading(true);
    setLoading(true);
    setActiveScenario("AI Custom Scenario");
    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";
      const response = await fetch(`${apiUrl}/simulate/ai`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          inventory: data.inventory,
          profile: data.profile,
          query: aiPrompt,
        }),
      });
      if (response.ok) {
        setResult(await response.json());
      } else {
        const errorData = await response.json();
        alert(errorData.detail?.message || "Failed to parse scenario.");
        setActiveScenario(null);
      }
    } catch (err) {
      console.error(err);
      setActiveScenario(null);
    } finally {
      setIsAILoading(false);
      setLoading(false);
    }
  };

  return {
    result,
    setResult,
    loading,
    activeScenario,
    setActiveScenario,
    isAILoading,
    runSimulation,
    runAISimulation,
  };
}
