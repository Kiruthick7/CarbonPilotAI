"use client";

import React from "react";

export interface Breakdown {
  category: string;
  total_kgco2e: number;
}

interface BeforeAfterChartProps {
  originalBreakdowns: Breakdown[];
  newBreakdowns: Breakdown[];
}

export function BeforeAfterChart({
  originalBreakdowns,
  newBreakdowns,
}: BeforeAfterChartProps) {
  const maxValue = Math.max(
    ...originalBreakdowns.map((b) => b.total_kgco2e),
    ...newBreakdowns.map((b) => b.total_kgco2e),
  );

  if (maxValue === 0) return null;

  return (
    <div className="w-full text-left mt-8 bg-black/20 p-6 rounded-2xl border border-white/5 backdrop-blur-md animate-in fade-in duration-500 slide-in-from-bottom-4">
      <h4 className="text-xs uppercase tracking-widest text-emerald-400/80 font-bold mb-6 flex items-center gap-2">
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
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
        Impact by Category
      </h4>
      <div className="space-y-5">
        {originalBreakdowns.map((orig, idx) => {
          const newBreakdown = newBreakdowns.find(
            (b) => b.category === orig.category,
          );
          const newKg = newBreakdown
            ? newBreakdown.total_kgco2e
            : orig.total_kgco2e;

          if (orig.total_kgco2e <= 0) return null;

          const origPercent = (orig.total_kgco2e / maxValue) * 100;
          const newPercent = (newKg / maxValue) * 100;
          const reduced = newKg < orig.total_kgco2e;
          const reductionPercent =
            ((orig.total_kgco2e - newKg) / orig.total_kgco2e) * 100;

          return (
            <div key={idx} className="w-full group">
              <div className="flex justify-between items-end mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-slate-300 capitalize">
                    {orig.category}
                  </span>
                  {reduced && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/20 opacity-0 group-hover:opacity-100 transition-opacity">
                      -{reductionPercent.toFixed(0)}%
                    </span>
                  )}
                </div>
                <div className="text-xs font-mono text-right flex gap-2">
                  <span
                    className={
                      reduced ? "text-slate-500 line-through" : "text-slate-400"
                    }
                  >
                    {(orig.total_kgco2e / 1000).toFixed(2)}
                  </span>
                  {reduced && (
                    <span className="text-emerald-400 font-bold">
                      {(newKg / 1000).toFixed(2)} t
                    </span>
                  )}
                </div>
              </div>
              <div className="relative w-full h-3.5 bg-white/5 rounded-full overflow-hidden border border-white/5">
                <div
                  className="absolute top-0 left-0 h-full bg-slate-600/40 rounded-full transition-all duration-700 ease-out"
                  style={{ width: `${origPercent}%` }}
                />
                <div
                  className="absolute top-0 left-0 h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full transition-all duration-1000 delay-150 ease-out shadow-[0_0_12px_rgba(16,185,129,0.4)]"
                  style={{ width: `${newPercent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
