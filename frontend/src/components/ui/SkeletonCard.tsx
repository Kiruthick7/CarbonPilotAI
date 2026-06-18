import React from "react";

export function SkeletonCard() {
  return (
    <div
      className="mt-4 p-6 bg-slate-50 rounded-xl border border-slate-200 animate-pulse"
      aria-hidden="true"
      aria-busy="true"
    >
      <div className="h-6 bg-slate-200 rounded w-1/3 mb-4"></div>
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="h-20 bg-slate-200 rounded-lg"></div>
        <div className="h-20 bg-slate-200 rounded-lg"></div>
        <div className="h-20 bg-slate-200 rounded-lg"></div>
      </div>
      <div className="space-y-3">
        <div className="h-4 bg-slate-200 rounded w-3/4"></div>
        <div className="h-4 bg-slate-200 rounded w-2/3"></div>
        <div className="h-4 bg-slate-200 rounded w-5/6"></div>
      </div>
    </div>
  );
}
