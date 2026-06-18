interface ExecutionPlanHeaderProps {
  title: string;
  timelineWeeks: string;
}

export function ExecutionPlanHeader({
  title,
  timelineWeeks,
}: ExecutionPlanHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-6">
      <h4 className="text-lg font-bold text-slate-900">
        Execution Plan: {title}
      </h4>
      <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
        Timeline: {timelineWeeks}
      </span>
    </div>
  );
}
