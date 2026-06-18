import React from "react";

interface DigitalFootprintFormProps {
  deviceFrequency: string;
  setDeviceFrequency: (val: string) => void;
  streamingUsage: string;
  setStreamingUsage: (val: string) => void;
  aiUsage: string;
  setAiUsage: (val: string) => void;
  error: string | null;
  isUploading: boolean;
  handleDigitalSubmit: () => void;
}

export function DigitalFootprintForm({
  deviceFrequency,
  setDeviceFrequency,
  streamingUsage,
  setStreamingUsage,
  aiUsage,
  setAiUsage,
  error,
  isUploading,
  handleDigitalSubmit,
}: DigitalFootprintFormProps) {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <label htmlFor="deviceFrequency" className="block text-sm font-bold text-slate-700 mb-2">
          How often do you replace your primary devices (phone/laptop)?
        </label>
        <select
          id="deviceFrequency"
          name="deviceFrequency"
          value={deviceFrequency}
          onChange={(e) => setDeviceFrequency(e.target.value)}
          className="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-900 focus:ring-2 focus:ring-emerald-500 outline-none"
        >
          <option value="frequent">Every 1-2 years (Frequent)</option>
          <option value="average">Every 3-4 years (Average)</option>
          <option value="rare">Every 5+ years (Rare)</option>
        </select>
      </div>
      <div>
        <label htmlFor="streamingUsage" className="block text-sm font-bold text-slate-700 mb-2">
          Daily heavy bandwidth usage (Netflix, Gaming)
        </label>
        <select
          id="streamingUsage"
          name="streamingUsage"
          value={streamingUsage}
          onChange={(e) => setStreamingUsage(e.target.value)}
          className="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-900 focus:ring-2 focus:ring-emerald-500 outline-none"
        >
          <option value="light">Light (&lt; 1 hr)</option>
          <option value="moderate">Moderate (2-4 hrs)</option>
          <option value="heavy">Heavy (5+ hrs)</option>
        </select>
      </div>
      <div>
        <label htmlFor="aiUsage" className="block text-sm font-bold text-slate-700 mb-2">
          Daily generative AI & heavy cloud computing
        </label>
        <select
          id="aiUsage"
          name="aiUsage"
          value={aiUsage}
          onChange={(e) => setAiUsage(e.target.value)}
          className="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-900 focus:ring-2 focus:ring-emerald-500 outline-none"
        >
          <option value="rare">Rare (A few times a week)</option>
          <option value="occasional">Occasional (1-5 times a day)</option>
          <option value="heavy">Heavy User (Multiple times a day)</option>
        </select>
      </div>
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
          {error}
        </div>
      )}
      <button
        onClick={handleDigitalSubmit}
        disabled={isUploading}
        className="w-full mt-4 bg-emerald-600 text-white rounded-xl py-3.5 font-bold shadow-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
      >
        {isUploading ? "Calculating..." : "Finish & View Dashboard"}
      </button>
    </div>
  );
}
