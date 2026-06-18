interface ExecutionPlanMetricsProps {
  carbonSavings: number;
  financialSavings: number;
  paybackPeriod: number | null;
}

export function ExecutionPlanMetrics({
  carbonSavings,
  financialSavings,
  paybackPeriod,
}: ExecutionPlanMetricsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm text-center">
        <p className="text-sm text-slate-500 font-semibold mb-1 uppercase tracking-wider">
          Carbon Impact
        </p>
        <p className="text-2xl font-bold text-emerald-600">
          ↓ {carbonSavings}{" "}
          <span className="text-sm font-medium">tCO₂e/yr</span>
        </p>
      </div>
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm text-center">
        <p className="text-sm text-slate-500 font-semibold mb-1 uppercase tracking-wider">
          Financial ROI
        </p>
        <p className="text-2xl font-bold text-green-600">
          {financialSavings > 0 ? `+$${financialSavings}` : "N/A"}{" "}
          <span className="text-sm font-medium">/yr</span>
        </p>
      </div>
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm text-center">
        <p className="text-sm text-slate-500 font-semibold mb-1 uppercase tracking-wider">
          Payback Period
        </p>
        <p className="text-2xl font-bold text-blue-600">
          {paybackPeriod !== null ? `${paybackPeriod} yrs` : "Immediate"}
        </p>
      </div>
    </div>
  );
}
