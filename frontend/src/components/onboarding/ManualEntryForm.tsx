import React from "react";

const US_NATIONAL_AVERAGE_KWH_MONTH = 877;

interface ManualEntryFormProps {
  manualKwh: string;
  setManualKwh: (val: string) => void;
  handleManualSubmit: (e?: React.MouseEvent, overrideKwh?: string) => void;
  isUploading: boolean;
}

export function ManualEntryForm({
  manualKwh,
  setManualKwh,
  handleManualSubmit,
  isUploading,
}: ManualEntryFormProps) {
  return (
    <div className="space-y-4 mb-6">
      <div>
        <label htmlFor="manual-kwh-input" className="block text-sm font-medium text-slate-700 mb-1">
          Monthly Electricity Usage (kWh)
        </label>
        <input
          id="manual-kwh-input"
          name="manual-kwh"
          type="number"
          value={manualKwh}
          onChange={(e) => setManualKwh(e.target.value)}
          placeholder="e.g. 450"
          className="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 outline-none"
        />
      </div>
      <button
        onClick={handleManualSubmit}
        disabled={!manualKwh || isUploading}
        className="w-full mt-4 bg-emerald-600 text-white rounded-xl py-3.5 font-bold shadow-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
      >
        Generate Carbon Profile
      </button>
      <button
        onClick={() =>
          handleManualSubmit(
            undefined,
            US_NATIONAL_AVERAGE_KWH_MONTH.toString(),
          )
        }
        disabled={isUploading}
        className="w-full mt-2 bg-slate-100 text-slate-600 rounded-xl py-3 font-semibold shadow-sm hover:bg-slate-200 disabled:opacity-50 transition-colors"
      >
        Don&apos;t know? Use National Average
      </button>
    </div>
  );
}
