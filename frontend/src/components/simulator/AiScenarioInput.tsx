import React from "react";

interface AiScenarioInputProps {
  aiPrompt: string;
  setAiPrompt: (val: string) => void;
  runAISimulation: (prompt: string) => void;
  isAILoading: boolean;
}

export function AiScenarioInput({
  aiPrompt,
  setAiPrompt,
  runAISimulation,
  isAILoading,
}: AiScenarioInputProps) {
  const handleSimulate = () => {
    const trimmed = aiPrompt.trim();
    if (trimmed) {
      runAISimulation(trimmed);
    }
  };

  return (
    <div
      className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 shadow-inner"
      role="region"
      aria-label="AI Scenario Assistant"
    >
      <h2 className="text-lg font-bold text-emerald-800 mb-2 flex items-center gap-2">
        <svg
          aria-hidden="true"
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
        Ask the AI Assistant
      </h2>
      <p className="text-sm text-emerald-600 mb-3">
        Try asking to combine multiple changes, like: &quot;What if I switch to
        a vegan diet and install solar panels?&quot;
      </p>
      <label htmlFor="ai-prompt-input" className="sr-only">
        Describe multiple climate actions
      </label>
      <div className="flex gap-2">
        <input
          id="ai-prompt-input"
          type="text"
          value={aiPrompt}
          onChange={(e) => setAiPrompt(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSimulate()}
          placeholder="e.g. Switch to an EV and reduce my long haul flights by 2"
          className="flex-1 px-4 py-2 rounded-xl border border-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm"
          aria-invalid={!aiPrompt.trim() ? "true" : "false"}
          maxLength={200}
        />
        <button
          onClick={handleSimulate}
          disabled={isAILoading || !aiPrompt.trim()}
          className="bg-emerald-600 text-white px-5 py-2 rounded-xl font-bold shadow-md hover:bg-emerald-700 disabled:opacity-50"
          aria-busy={isAILoading}
          aria-live="polite"
        >
          {isAILoading ? "Thinking..." : "Simulate"}
        </button>
      </div>
      <p className="text-xs text-emerald-600 mt-2 bg-emerald-100/50 p-2 rounded-lg inline-block border border-emerald-200/50">
        <span className="font-bold">Tip:</span> Phrase scenarios as lifestyle
        reductions (e.g. &quot;Switch to an EV&quot; or &quot;Eat less
        meat&quot;) rather than raw additions.
      </p>
    </div>
  );
}
