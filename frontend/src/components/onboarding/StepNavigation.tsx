interface StepNavigationProps {
  entryMode: "upload" | "manual";
  setEntryMode: (mode: "upload" | "manual") => void;
}

export function StepNavigation({
  entryMode,
  setEntryMode,
}: StepNavigationProps) {
  return (
    <div className="flex bg-slate-100 p-1 rounded-xl mb-6">
      <button
        className={`flex-1 py-2 text-sm font-bold rounded-lg ${entryMode === "upload" ? "bg-white shadow text-emerald-700" : "text-slate-500"}`}
        onClick={() => setEntryMode("upload")}
      >
        Upload Bill
      </button>
      <button
        className={`flex-1 py-2 text-sm font-bold rounded-lg ${entryMode === "manual" ? "bg-white shadow text-emerald-700" : "text-slate-500"}`}
        onClick={() => setEntryMode("manual")}
      >
        Enter Manually
      </button>
    </div>
  );
}
