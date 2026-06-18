import { MathTooltip } from "@/components/MathTooltip";
import { OcrData } from "@/context/CarbonDataContext";

interface DashboardSummaryProps {
  currentData: OcrData;
}

export function DashboardSummary({ currentData }: DashboardSummaryProps) {
  return (
    <div className="bg-[#00D287] p-6 rounded-xl shadow-sm border col-span-1 text-white relative flex flex-col justify-center h-48">
      <div className="absolute inset-0 overflow-hidden rounded-xl pointer-events-none">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl -mr-10 -mt-10" />
      </div>
      <h3 className="text-sm font-bold uppercase tracking-wider mb-2 opacity-90 relative">
        Total Baseline Footprint
      </h3>
      <div className="text-6xl font-black tracking-tighter mb-1 flex items-baseline">
        {currentData.inventory ? (
          <MathTooltip trace={currentData.inventory.trace}>
            {currentData.inventory.total_tco2e.toFixed(2)}
          </MathTooltip>
        ) : (
          (currentData.calculated_footprint_tco2e || 0).toFixed(2)
        )}
        <span className="text-2xl font-semibold opacity-80 ml-1 flex items-center gap-1 relative group">
          tCO₂e
          <svg
            className="w-5 h-5 opacity-80 cursor-help hover:opacity-100 transition-opacity"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 w-64 bg-slate-900 text-white text-sm font-normal tracking-normal leading-relaxed rounded-xl p-4 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 shadow-2xl pointer-events-none">
            <span className="block font-bold mb-1 text-emerald-400">
              What is tCO₂e?
            </span>
            Tonnes of Carbon Dioxide Equivalent is a standard unit for counting
            all greenhouse gas emissions.
            <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-slate-900"></div>
          </div>
        </span>
      </div>
      <p className="text-sm opacity-80 mt-2 leading-tight max-w-[200px]">
        Calculated dynamically from {currentData.kwh_usage} kWh local utility
        usage and default profile.
      </p>
    </div>
  );
}
