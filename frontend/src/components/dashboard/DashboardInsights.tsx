import { OcrData } from "@/context/CarbonDataContext";

interface DashboardInsightsProps {
  currentData: OcrData;
  totalKg: number;
}

export function DashboardInsights({
  currentData,
  totalKg,
}: DashboardInsightsProps) {
  if (!currentData.inventory) return null;

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border mb-8">
      <h2 className="text-xl font-bold mb-6">Emissions Breakdown</h2>

      <div className="mb-8">
        <h3 className="text-sm font-bold text-emerald-600 uppercase tracking-wider mb-4 flex items-center gap-2">
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
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          Verified Data (From Utility Bill)
        </h3>
        <div className="space-y-5">
          {currentData.inventory.breakdowns
            .filter((cat) => cat.total_kgco2e > 0)
            .map((cat) => {
              const percentage =
                totalKg > 0 ? (cat.total_kgco2e / totalKg) * 100 : 0;
              return (
                <div key={cat.category}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700 capitalize">
                      {cat.category}
                    </span>
                    <span className="text-gray-500 font-semibold">
                      {(cat.total_kgco2e / 1000).toFixed(2)} tCO₂e (
                      {percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2.5">
                    <div
                      className="bg-emerald-500 h-2.5 rounded-full transition-all duration-1000 ease-out"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {currentData.inventory.breakdowns.filter((cat) => cat.total_kgco2e === 0)
        .length > 0 && (
        <div className="pt-6 border-t border-gray-100">
          <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
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
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Estimated Data (Default Profile)
          </h3>
          <div className="space-y-5">
            {currentData.inventory.breakdowns
              .filter((cat) => cat.total_kgco2e === 0)
              .map((cat) => {
                const percentage =
                  totalKg > 0 ? (cat.total_kgco2e / totalKg) * 100 : 0;
                return (
                  <div key={cat.category} className="opacity-70">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-gray-700 capitalize">
                        {cat.category}
                      </span>
                      <span className="text-gray-500 font-semibold">
                        {(cat.total_kgco2e / 1000).toFixed(2)} tCO₂e (
                        {percentage.toFixed(0)}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2.5">
                      <div
                        className="bg-gray-400 h-2.5 rounded-full transition-all duration-1000 ease-out"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}
