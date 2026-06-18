import { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: ReactNode;
  subtitle?: string;
  icon?: ReactNode;
  className?: string;
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon,
  className = "",
}: MetricCardProps) {
  return (
    <div
      className={`bg-white p-6 rounded-xl shadow-sm border border-slate-200 col-span-1 flex flex-col justify-center h-48 ${className}`}
    >
      {icon && (
        <div className="flex items-center gap-3 mb-6">
          <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-500">
            {icon}
          </div>
          <h3 className="text-lg font-bold text-gray-900">{title}</h3>
        </div>
      )}
      {!icon && (
        <h3 className="text-sm font-bold uppercase tracking-wider mb-2 opacity-90 relative">
          {title}
        </h3>
      )}
      <div className="text-4xl font-black tracking-tighter mb-1 flex items-baseline">
        {value}
      </div>
      {subtitle && (
        <p className="text-sm opacity-80 mt-2 leading-tight max-w-[200px]">
          {subtitle}
        </p>
      )}
    </div>
  );
}
