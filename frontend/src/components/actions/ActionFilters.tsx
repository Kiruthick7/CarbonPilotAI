import { OcrData } from "@/context/CarbonDataContext";

interface ActionFiltersProps {
  ocrData: OcrData | null;
  activeView: number | "combined";
  setActiveView: (view: number | "combined") => void;
}

export function ActionFilters({
  ocrData,
  activeView,
  setActiveView,
}: ActionFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0 w-full md:w-auto md:ml-4">
      {ocrData?.individual_results && ocrData.individual_results.length > 1 && (
        <select
          id="action-view-select"
          name="action-view-select"
          value={activeView}
          onChange={(e) =>
            setActiveView(
              e.target.value === "combined"
                ? "combined"
                : parseInt(e.target.value),
            )
          }
          className="bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 font-medium shadow-sm outline-none print:hidden"
        >
          <option value="combined">Combined View (All Files)</option>
          {ocrData.individual_results.map((result, idx: number) => (
            <option key={idx} value={idx}>
              File: {result.filename}
            </option>
          ))}
        </select>
      )}
      <button
        onClick={() => window.print()}
        className="flex items-center gap-2 bg-slate-900 text-white px-4 py-2.5 rounded-lg text-sm font-semibold shadow-sm hover:bg-slate-800 transition print:hidden"
        aria-label="Export Action Plan as PDF"
      >
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
            d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        Export PDF
      </button>
    </div>
  );
}
