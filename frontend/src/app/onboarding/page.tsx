"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCarbonData, OcrData } from "@/context/CarbonDataContext";
import { DEMO_CARBON_PROFILE_DATA } from "@/constants/mockData";
import { carbonApi } from "@/services/api";
import { useFileUpload } from "@/hooks/useFileUpload";
import { FileUploadZone } from "@/components/onboarding/FileUploadZone";
import { ManualEntryForm } from "@/components/onboarding/ManualEntryForm";
import { DigitalFootprintForm } from "@/components/onboarding/DigitalFootprintForm";

import { CarbonProfile } from "@/types/carbon";

export default function OnboardingPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { setOcrData } = useCarbonData();
  const [consentGiven, setConsentGiven] = useState(false);
  const [entryMode, setEntryMode] = useState<'upload' | 'manual'>('upload');
  const [manualKwh, setManualKwh] = useState("");
  
  const [step, setStep] = useState<'upload' | 'digital'>('upload');
  const [tempOcrData, setTempOcrData] = useState<OcrData | null>(null);

  const [deviceFrequency, setDeviceFrequency] = useState('average');
  const [streamingUsage, setStreamingUsage] = useState('moderate');
  const [aiUsage, setAiUsage] = useState('occasional');

  const { files, fileInputRef, handleFileChange, removeFile, handleUploadClick } = useFileUpload(isUploading);

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
      const data = await carbonApi.uploadUtilityBills(files);
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
      const data = await carbonApi.submitManualEntry(parseFloat(valueToUse));
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
    setTempOcrData(DEMO_CARBON_PROFILE_DATA as unknown as OcrData);
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
      
      const data = await carbonApi.calculateDigitalFootprint(updatedProfile as CarbonProfile);
      
      const finalOcrData: OcrData = {
        ...tempOcrData,
        profile: updatedProfile as CarbonProfile,
        inventory: data.inventory,
        individual_results: tempOcrData.individual_results
      };
      
      setOcrData(finalOcrData);
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
          <DigitalFootprintForm 
            deviceFrequency={deviceFrequency}
            setDeviceFrequency={setDeviceFrequency}
            streamingUsage={streamingUsage}
            setStreamingUsage={setStreamingUsage}
            aiUsage={aiUsage}
            setAiUsage={setAiUsage}
            error={error}
            isUploading={isUploading}
            handleDigitalSubmit={handleDigitalSubmit}
          />
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
              <ManualEntryForm 
                manualKwh={manualKwh}
                setManualKwh={setManualKwh}
                handleManualSubmit={handleManualSubmit}
                isUploading={isUploading}
              />
            ) : (
              <>
                <FileUploadZone 
                  files={files}
                  isUploading={isUploading}
                  fileInputRef={fileInputRef}
                  handleFileChange={handleFileChange}
                  removeFile={removeFile}
                  handleUploadClick={handleUploadClick}
                  handleKeyDown={handleKeyDown}
                />
                
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
