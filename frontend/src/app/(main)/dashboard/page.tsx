"use client";


import { MathTooltip } from "@/components/MathTooltip";

import { useCarbonData } from "@/context/CarbonDataContext";

export default function DashboardPage() {
  const { ocrData, isHydrated, actionsView: activeView, setActionsView: setActiveView } = useCarbonData();

  if (!isHydrated) {
    return (
      <div className="flex justify-center py-10">
        <svg className="animate-spin h-8 w-8 text-emerald-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    );
  }

  if (!ocrData) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">No data found. Please complete the Onboarding step.</p>
      </div>
    );
  }

  
  const currentData = activeView === "combined" 
    ? ocrData 
    : (ocrData.individual_results?.[activeView as number] || ocrData);

  
  const totalKg = (currentData.inventory?.total_tco2e || 0) * 1000;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        {ocrData.individual_results && ocrData.individual_results.length > 1 && (
          <select
            value={activeView}
            onChange={(e) => setActiveView(e.target.value === "combined" ? "combined" : parseInt(e.target.value))}
            className="bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 font-medium shadow-sm outline-none"
          >
            <option value="combined">Combined View (All Files)</option>
            {ocrData.individual_results.map((result, idx) => (
              <option key={idx} value={idx}>File: {result.filename}</option>
            ))}
          </select>
        )}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-[#00D287] p-6 rounded-xl shadow-sm border col-span-1 text-white relative flex flex-col justify-center h-48">
          <div className="absolute inset-0 overflow-hidden rounded-xl pointer-events-none">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl -mr-10 -mt-10" />
          </div>
          <h3 className="text-sm font-bold uppercase tracking-wider mb-2 opacity-90 relative">Total Baseline Footprint</h3>
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
              <svg className="w-5 h-5 opacity-80 cursor-help hover:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 w-64 bg-slate-900 text-white text-sm font-normal tracking-normal leading-relaxed rounded-xl p-4 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 shadow-2xl pointer-events-none">
                <span className="block font-bold mb-1 text-emerald-400">What is tCO₂e?</span>
                Tonnes of Carbon Dioxide Equivalent is a standard unit for counting all greenhouse gas emissions.
                <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-slate-900"></div>
              </div>
            </span>
          </div>
          <p className="text-sm opacity-80 mt-2 leading-tight max-w-[200px]">Calculated dynamically from {currentData.kwh_usage} kWh local utility usage and default profile.</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border col-span-1 md:col-span-2 flex flex-col justify-center h-48">
          <div className="flex items-center gap-3 mb-6">
             <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-500">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
             </div>
             <h3 className="text-lg font-bold text-gray-900">Utility Bill Data</h3>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-gray-400 font-semibold mb-1">Source File</p>
              <p className="font-bold text-gray-800 truncate">{currentData.filename}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 font-semibold mb-1">Energy Usage</p>
              <p className="font-bold text-gray-800">{currentData.kwh_usage} <span className="text-gray-400 font-normal">kWh</span></p>
            </div>
            <div>
              <p className="text-xs text-gray-400 font-semibold mb-1">Total Cost</p>
              <p className="font-bold text-gray-800">{currentData.total_cost_usd ? `$${currentData.total_cost_usd}` : 'N/A'}</p>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-3">
             <p className="text-xs text-gray-400 font-semibold w-24">OCR Confidence</p>
             <div className="flex-1 bg-gray-100 h-2 rounded-full overflow-hidden max-w-[150px]">
               <div className="bg-amber-400 h-full rounded-full" style={{ width: `${(currentData.confidence || 0) * 100}%` }}></div>
             </div>
             <span className="text-xs font-bold text-gray-600">{Math.round((currentData.confidence || 0) * 100)}%</span>
          </div>
        </div>
      </div>
      

      {currentData.inventory && (
        <div className="bg-white p-6 rounded-xl shadow-sm border mb-8">
          <h2 className="text-xl font-bold mb-6">Emissions Breakdown</h2>
          
          <div className="mb-8">
            <h3 className="text-sm font-bold text-emerald-600 uppercase tracking-wider mb-4 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              Verified Data (From Utility Bill)
            </h3>
            <div className="space-y-5">
              {currentData.inventory.breakdowns.filter(cat => cat.total_kgco2e > 0).map((cat) => {
                const percentage = totalKg > 0 ? (cat.total_kgco2e / totalKg) * 100 : 0;
                return (
                  <div key={cat.category}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-gray-700 capitalize">{cat.category}</span>
                      <span className="text-gray-500 font-semibold">{(cat.total_kgco2e / 1000).toFixed(2)} tCO₂e ({percentage.toFixed(0)}%)</span>
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

          {currentData.inventory.breakdowns.filter(cat => cat.total_kgco2e === 0).length > 0 && (
            <div className="pt-6 border-t border-gray-100">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                Estimated Data (Default Profile)
              </h3>
              <div className="space-y-5">
                {currentData.inventory.breakdowns.filter(cat => cat.total_kgco2e === 0).map((cat) => {
                  const percentage = totalKg > 0 ? (cat.total_kgco2e / totalKg) * 100 : 0;
                  return (
                    <div key={cat.category} className="opacity-70">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium text-gray-700 capitalize">{cat.category}</span>
                        <span className="text-gray-500 font-semibold">{(cat.total_kgco2e / 1000).toFixed(2)} tCO₂e ({percentage.toFixed(0)}%)</span>
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
      )}
    </div>
  );
}
