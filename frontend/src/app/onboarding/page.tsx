"use client";


import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useCarbonData, OcrData } from "@/context/CarbonDataContext";

type Breakdown = { category: string; total_kgco2e: number; [key: string]: unknown };
type IndividualResult = { inventory?: { breakdowns?: Breakdown[]; [key: string]: unknown }; [key: string]: unknown };

export default function OnboardingPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { setOcrData } = useCarbonData();
  const [consentGiven, setConsentGiven] = useState(false);
  const [entryMode, setEntryMode] = useState<'upload' | 'manual'>('upload');
  const [manualKwh, setManualKwh] = useState("");
  
  const [step, setStep] = useState<'upload' | 'digital'>('upload');
  const [tempOcrData, setTempOcrData] = useState<{
    profile?: Record<string, unknown>;
    inventory?: Record<string, unknown>;
    [key: string]: unknown;
  } | null>(null);
  const [deviceFrequency, setDeviceFrequency] = useState('average');
  const [streamingUsage, setStreamingUsage] = useState('moderate');
  const [aiUsage, setAiUsage] = useState('occasional');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      
      const validFiles = newFiles.filter(f => {
        const isValidType = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'].includes(f.type);
        const isValidSize = f.size <= 5 * 1024 * 1024;
        if (!isValidType) alert(`Invalid file type: ${f.name}`);
        if (!isValidSize) alert(`File too large (max 5MB): ${f.name}`);
        return isValidType && isValidSize;
      });

      setFiles(prev => {
        const existingNames = new Set(prev.map(f => f.name));
        const uniqueNewFiles = validFiles.filter(f => !existingNames.has(f.name));
        return [...prev, ...uniqueNewFiles];
      });
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const removeFile = (indexToRemove: number) => {
    setFiles(prev => prev.filter((_, i) => i !== indexToRemove));
  };

  const handleUploadClick = () => {
    if (!isUploading) fileInputRef.current?.click();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleUploadClick();
    }
  };

  const handleContinue = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (files.length === 0) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      files.forEach(f => formData.append("files", f));
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";
      const response = await fetch(`${apiUrl}/ocr/upload`, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error("Failed to process document locally.");
      }
      
      const data = await response.json();
      
      setTempOcrData(data);
      setStep('digital');
      setIsUploading(false);
    } catch (err: unknown) {
      console.error(err);
      setError((err as Error).message || "An unexpected error occurred.");
      setIsUploading(false);
    }
  };

  const handleManualSubmit = async (e?: React.MouseEvent, overrideKwh?: string) => {
    e?.preventDefault();
    const valueToUse = overrideKwh || manualKwh;
    if (!valueToUse) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";
      const response = await fetch(`${apiUrl}/ocr/manual`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kwh_usage: parseFloat(valueToUse) }),
      });
      
      if (!response.ok) {
        throw new Error("Failed to process manual entry.");
      }
      
      const data = await response.json();
      setTempOcrData(data);
      setStep('digital');
      setIsUploading(false);
    } catch (err: unknown) {
      console.error(err);
      setError((err as Error).message || "An unexpected error occurred.");
      setIsUploading(false);
    }
  };

  const handleLoadDemoProfile = () => {
    const demoData = {
      "success":true,"filename":"sample_bill.pdf","kwh_usage":450.0,"total_cost_usd":135.0,"confidence":1.0,"calculated_footprint_tco2e":0.173,
      "profile":{"country_code":"US","transport":null,"diet":null,"home":{"home_size":"medium","heating_type":"gas","num_occupants":2,"has_solar":false,"renewable_tariff":false},"consumption":null},
      "inventory":{"total_tco2e":7.72,"breakdowns":[{"category":"transport","total_kgco2e":1820.0,"subcategories":[{"label":"Car","kgco2e":1820.0,"share_of_category":1.0},{"label":"Short-haul flights","kgco2e":0.0,"share_of_category":0.0},{"label":"Long-haul flights","kgco2e":0.0,"share_of_category":0.0},{"label":"Public transport","kgco2e":0.0,"share_of_category":0.0}]},{"category":"diet","total_kgco2e":2310.0,"subcategories":[{"label":"Food production","kgco2e":2310.0,"share_of_category":1.0},{"label":"Food waste","kgco2e":0.0,"share_of_category":0.0}]},{"category":"home","total_kgco2e":2450.0,"subcategories":[{"label":"Heating","kgco2e":0.0,"share_of_category":0.0},{"label":"Electricity","kgco2e":2450.0,"share_of_category":1.0}]},{"category":"consumption","total_kgco2e":1140.0,"subcategories":[{"label":"Clothing","kgco2e":1140.0,"share_of_category":1.0},{"label":"Electronics","kgco2e":0.0,"share_of_category":0.0},{"label":"Deliveries","kgco2e":0.0,"share_of_category":0.0}]}],"national_average_tco2e":4.8,"global_average_tco2e":4.8,"budget_1_5c_tco2e":2.3}
    };
    setTempOcrData(demoData);
    setStep('digital');
  };

  const handleDigitalSubmit = async () => {
    if (!tempOcrData) return;
    setIsUploading(true);
    setError(null);
    try {
      const updatedProfile = {
        ...tempOcrData.profile,
        digital: {
          device_upgrade_frequency: deviceFrequency,
          streaming_gaming_usage: streamingUsage,
          ai_cloud_usage: aiUsage
        }
      };
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";
      const response = await fetch(`${apiUrl}/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedProfile),
      });
      
      if (!response.ok) {
        throw new Error("Failed to process digital footprint.");
      }
      
      const data = await response.json();
      
      // Extract just the digital breakdown from the pure theoretical calculation
      const digitalBreakdown = data.inventory.breakdowns.find((b: Breakdown) => b.category === "digital");
      
      // Keep existing inventory (with OCR overrides) but update digital
      // Keep existing inventory (with OCR overrides) but update digital
      const newBreakdowns = ((tempOcrData.inventory?.breakdowns as Breakdown[]) || []).filter((b: Breakdown) => b.category !== "digital");
      if (digitalBreakdown) {
        newBreakdowns.push(digitalBreakdown);
      }
      
      // Recalculate total tCO2e
      const newTotalKg = newBreakdowns.reduce((sum: number, b: Breakdown) => sum + b.total_kgco2e, 0);
      
      const finalOcrData = {
        ...tempOcrData,
        profile: updatedProfile,
        inventory: {
          ...tempOcrData.inventory,
          breakdowns: newBreakdowns,
          total_tco2e: Number((newTotalKg / 1000).toFixed(3))
        },
        individual_results: (tempOcrData.individual_results as IndividualResult[])?.map((res: IndividualResult) => {
          const resBreakdowns = ((res.inventory?.breakdowns as Breakdown[]) || []).filter((b: Breakdown) => b.category !== "digital");
          if (digitalBreakdown) resBreakdowns.push(digitalBreakdown);
          const resTotalKg = resBreakdowns.reduce((sum: number, b: Breakdown) => sum + b.total_kgco2e, 0);
          return {
            ...res,
            profile: updatedProfile,
            inventory: {
              ...res.inventory,
              breakdowns: resBreakdowns,
              total_tco2e: Number((resTotalKg / 1000).toFixed(3))
            }
          };
        })
      };
      
      setOcrData(finalOcrData as unknown as OcrData);
      router.push("/dashboard");
    } catch (err: unknown) {
      console.error(err);
      setError((err as Error).message || "An unexpected error occurred.");
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 font-sans relative overflow-hidden">
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-emerald-300/10 rounded-full blur-[80px] -z-10" />
      <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-blue-300/10 rounded-full blur-[80px] -z-10" />

      <div className="max-w-md w-full bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-200/50 p-10">
        <div className="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center mb-6">
           <svg className="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
           </svg>
        </div>
        <h1 className="text-3xl font-black mb-3 text-slate-900 tracking-tight">
          {step === 'digital' ? "Your Digital Footprint." : "Let's calculate your baseline."}
        </h1>
        <p className="text-slate-500 mb-8 leading-relaxed">
          {step === 'digital' 
            ? "Your screen time and device habits contribute to 'invisible' emissions. Let's estimate them." 
            : "Upload your recent utility bills or receipts to get started. We extract your usage to build your deterministic profile."}
        </p>
        
        {step === 'digital' ? (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">How often do you replace your primary devices (phone/laptop)?</label>
              <select value={deviceFrequency} onChange={e => setDeviceFrequency(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-900 focus:ring-2 focus:ring-emerald-500 outline-none">
                <option value="frequent">Every 1-2 years (Frequent)</option>
                <option value="average">Every 3-4 years (Average)</option>
                <option value="rare">Every 5+ years (Rare)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Daily heavy bandwidth usage (Netflix, Gaming)</label>
              <select value={streamingUsage} onChange={e => setStreamingUsage(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-900 focus:ring-2 focus:ring-emerald-500 outline-none">
                <option value="light">Light (&lt; 1 hr)</option>
                <option value="moderate">Moderate (2-4 hrs)</option>
                <option value="heavy">Heavy (5+ hrs)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Daily generative AI & heavy cloud computing</label>
              <select value={aiUsage} onChange={e => setAiUsage(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-900 focus:ring-2 focus:ring-emerald-500 outline-none">
                <option value="rare">Rare (A few times a week)</option>
                <option value="occasional">Occasional (1-5 times a day)</option>
                <option value="heavy">Heavy User (Multiple times a day)</option>
              </select>
            </div>
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                {error}
              </div>
            )}
            <button
              onClick={handleDigitalSubmit}
              disabled={isUploading}
              className="w-full mt-4 bg-emerald-600 text-white rounded-xl py-3.5 font-bold shadow-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            >
              {isUploading ? "Calculating..." : "Finish & View Dashboard"}
            </button>
          </div>
        ) : (
          <>
            <div className="flex bg-slate-100 p-1 rounded-xl mb-6">
          <button 
            className={`flex-1 py-2 text-sm font-bold rounded-lg ${entryMode === 'upload' ? 'bg-white shadow text-emerald-700' : 'text-slate-500'}`}
            onClick={() => setEntryMode('upload')}
          >
            Upload Bill
          </button>
          <button 
            className={`flex-1 py-2 text-sm font-bold rounded-lg ${entryMode === 'manual' ? 'bg-white shadow text-emerald-700' : 'text-slate-500'}`}
            onClick={() => setEntryMode('manual')}
          >
            Enter Manually
          </button>
        </div>

        <button 
          onClick={handleLoadDemoProfile}
          className="w-full mb-6 bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 py-3 rounded-xl font-bold text-sm transition-colors"
        >
          🚀 Judge Fast-Track: Load Demo Profile
        </button>

        {entryMode === 'manual' ? (
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Monthly Electricity Usage (kWh)</label>
              <input 
                type="number" 
                value={manualKwh} 
                onChange={(e) => setManualKwh(e.target.value)} 
                placeholder="e.g. 450"
                className="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>
            <button
              onClick={handleManualSubmit}
              disabled={!manualKwh || isUploading}
              className="w-full mt-4 bg-emerald-600 text-white rounded-xl py-3.5 font-bold shadow-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            >
              Generate Carbon Profile
            </button>
            <button
              onClick={() => handleManualSubmit(undefined, "877")}
              disabled={isUploading}
              className="w-full mt-2 bg-slate-100 text-slate-600 rounded-xl py-3 font-semibold shadow-sm hover:bg-slate-200 disabled:opacity-50 transition-colors"
            >
              Don&apos;t know? Use National Average
            </button>
          </div>
        ) : (
          <>
            <input 
              type="file" 
              multiple
              ref={fileInputRef} 
              onChange={handleFileChange} 
              className="hidden" 
              accept="application/pdf,image/png,image/jpeg,image/jpg"
            />

            <div 
              role="button"
              tabIndex={isUploading ? -1 : 0}
              onClick={handleUploadClick}
              onKeyDown={handleKeyDown}
              aria-label="Upload utility bills"
              className={`border-2 border-dashed rounded-2xl p-10 text-center mb-8 transition-all focus:outline-none focus:ring-4 focus:ring-emerald-500/50 ${
                isUploading
                  ? "border-emerald-500 bg-emerald-50 cursor-wait relative overflow-hidden"
                  : files.length > 0 
                    ? "border-emerald-500 bg-emerald-50 hover:bg-emerald-100 cursor-pointer" 
                    : "border-slate-300 hover:border-emerald-400 hover:bg-slate-50 cursor-pointer"
              }`}
            >
              {isUploading ? (
                <div className="flex flex-col items-center w-full">
                  <div className="absolute top-0 left-0 right-0 h-1 bg-emerald-400 animate-[scan_2s_ease-in-out_infinite]" style={{boxShadow: "0 0 10px 2px rgba(52, 211, 153, 0.5)"}}></div>
                  <svg className="w-12 h-12 text-emerald-500 mb-4 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-emerald-800 font-bold mb-2 animate-pulse">Running Local OCR Model...</span>
                  <p className="text-sm text-emerald-600/70">Extracting text, values, and vendor details</p>
                </div>
              ) : files.length > 0 ? (
                <div className="flex flex-col items-center w-full">
                  <svg className="w-12 h-12 text-emerald-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-emerald-800 font-bold mb-4">{files.length} file{files.length > 1 ? 's' : ''} selected</span>
                  <div className="flex flex-wrap gap-2 justify-center w-full max-h-[120px] overflow-y-auto pb-2">
                     {files.map((f, idx) => (
                       <div key={idx} className="bg-white border border-emerald-200 text-emerald-700 text-xs px-3 py-1.5 rounded-full flex items-center gap-2 shadow-sm">
                         <span className="max-w-[120px] truncate">{f.name}</span>
                         <button 
                           type="button"
                           onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                           className="hover:bg-emerald-100 rounded-full p-0.5 text-emerald-500 hover:text-emerald-800 transition-colors"
                         >
                           <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                         </button>
                       </div>
                     ))}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center">
                  <div className="w-14 h-14 bg-slate-100 rounded-full flex items-center justify-center mb-4 text-slate-400 group-hover:text-emerald-500 transition-colors">
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                  </div>
                  <span className="text-slate-700 font-semibold">Click to upload multiple bills (PDF/PNG)</span>
                  <p className="text-sm text-slate-400 mt-2">Personal data is scrubbed locally.</p>
                </div>
              )}
            </div>
            
            <div className="mt-4 mb-6 text-xs text-slate-500 flex items-center justify-center gap-2">
              <svg className="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
              <p><strong>Privacy Guarantee:</strong> Processed securely via in-memory server instances. All files are instantly deleted after extraction and never stored.</p>
            </div>
            
            <div className="mt-6 mb-4 flex items-start gap-3">
              <input 
                type="checkbox" 
                id="privacy-consent" 
                checked={consentGiven}
                onChange={(e) => setConsentGiven(e.target.checked)}
                className="mt-1 w-4 h-4 text-emerald-600 rounded focus:ring-emerald-500"
              />
              <label htmlFor="privacy-consent" className="text-sm text-slate-600">
                I consent to processing my uploaded files using OCR to extract energy consumption data. Files are processed in-memory and are <strong>never stored</strong> in any database.
              </label>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                {error}
              </div>
            )}
            
            <button 
              onClick={handleContinue}
              disabled={files.length === 0 || isUploading || !consentGiven}
              className={`w-full py-4 rounded-xl font-bold flex justify-center items-center transition-all ${
                files.length > 0 && !isUploading && consentGiven
                  ? "bg-emerald-500 text-white hover:bg-emerald-600 shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 hover:-translate-y-0.5 transform" 
                  : "bg-slate-100 text-slate-400 cursor-not-allowed"
              }`}
            >
              {isUploading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Scanning...
                </>
              ) : (
                 "Process & Continue"
              )}
            </button>
          </>
        )}
        </>
        )}
      </div>
    </div>
  );
}
