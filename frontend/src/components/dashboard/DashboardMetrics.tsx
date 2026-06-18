import { OcrData } from "@/context/CarbonDataContext";

interface DashboardMetricsProps {
  currentData: OcrData;
}

export function DashboardMetrics({ currentData }: DashboardMetricsProps) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border col-span-1 md:col-span-2 flex flex-col justify-center h-48">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-500">
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-bold text-gray-900">Utility Bill Data</h3>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-xs text-gray-400 font-semibold mb-1">
            Source File
          </p>
          <p className="font-bold text-gray-800 truncate">
            {currentData.filename}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400 font-semibold mb-1">
            Energy Usage
          </p>
          <p className="font-bold text-gray-800">
            {currentData.kwh_usage}{" "}
            <span className="text-gray-400 font-normal">kWh</span>
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400 font-semibold mb-1">Total Cost</p>
          <p className="font-bold text-gray-800">
            {currentData.total_cost_usd
              ? `$${currentData.total_cost_usd}`
              : "N/A"}
          </p>
        </div>
      </div>
      <div className="mt-6 flex items-center gap-3">
        <p className="text-xs text-gray-400 font-semibold w-24">
          OCR Confidence
        </p>
        <div className="flex-1 bg-gray-100 h-2 rounded-full overflow-hidden max-w-[150px]">
          <div
            className="bg-amber-400 h-full rounded-full"
            style={{ width: `${(currentData.confidence || 0) * 100}%` }}
          ></div>
        </div>
        <span className="text-xs font-bold text-gray-600">
          {Math.round((currentData.confidence || 0) * 100)}%
        </span>
      </div>
    </div>
  );
}
