"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface RankedAction {
  id: string;
  title: string;
  description: string;
  effort_score: number;
  category: string;
  co2e_saved_per_year: number;
  upfront_cost_usd?: number;
  annual_saving_usd?: number;
  composite_score: number;
  why_recommended: string;
}

export interface OcrData {
  success?: boolean;
  filename?: string;
  kwh_usage?: number;
  total_cost_usd?: number | null;
  confidence?: number;
  calculated_footprint_tco2e?: number;
  inventory: {
    total_tco2e: number;
    trace?: {
      formula: string;
      variables: Record<string, string>;
      source: string;
    };
    breakdowns: Array<{
      category: string;
      total_kgco2e: number;
    }>;
    [key: string]: unknown;
  };
  profile: Record<string, unknown>;
  individual_results?: (OcrData & { filename: string })[];
  [key: string]: unknown;
}

interface CarbonContextType {
  ocrData: OcrData | null;
  setOcrData: (data: OcrData | null) => void;
  actions: RankedAction[];
  loadingActions: boolean;
  actionsView: "combined" | number;
  setActionsView: (view: "combined" | number) => void;
  isHydrated: boolean;
}

const CarbonContext = createContext<CarbonContextType | undefined>(undefined);

export function CarbonDataProvider({ children }: { children: ReactNode }) {
  const [ocrData, setOcrDataState] = useState<OcrData | null>(null);
  const [actions, setActions] = useState<RankedAction[]>([]);
  const [loadingActions, setLoadingActions] = useState(false);
  const [actionsView, setActionsView] = useState<"combined" | number>("combined");
  const [isHydrated, setIsHydrated] = useState(false);

  // Load from local storage on mount
  useEffect(() => {
    const dataStr = localStorage.getItem("carbonpilot_ocr_data");
    if (dataStr) {
      try {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setOcrDataState(JSON.parse(dataStr));
      } catch (e) {
        console.error("Failed to parse OCR data", e);
      }
    }
    setIsHydrated(true);
  }, []);

  const setOcrData = (data: OcrData | null) => {
    setOcrDataState(data);
    if (data) {
      localStorage.setItem("carbonpilot_ocr_data", JSON.stringify(data));
    } else {
      localStorage.removeItem("carbonpilot_ocr_data");
    }
  };

  // Fetch actions whenever ocrData or actionsView changes
  useEffect(() => {
    async function fetchActions() {
      if (!ocrData || !ocrData.inventory || !ocrData.profile) {
        setActions([]);
        return;
      }
      
      setLoadingActions(true);
      try {
        const currentData = actionsView === "combined" 
          ? ocrData
          : (ocrData.individual_results?.[actionsView as number] || ocrData);

        if (!currentData.inventory || !currentData.profile) {
          setActions([]);
          setLoadingActions(false);
          return;
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";
        const response = await fetch(`${apiUrl}/actions/rank`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            inventory: currentData.inventory,
            profile: currentData.profile,
            constraints: {}
          })
        });

        if (response.ok) {
          const result = await response.json();
          setActions(result.actions || []);
        } else {
          setActions([]);
        }
      } catch (err) {
        console.error("Failed to fetch actions:", err);
        setActions([]);
      } finally {
        setLoadingActions(false);
      }
    }

    // Debounce or just wait for hydration
    if (isHydrated) {
      fetchActions();
    }
  }, [ocrData, actionsView, isHydrated]);

  return (
    <CarbonContext.Provider value={{ ocrData, setOcrData, actions, loadingActions, actionsView, setActionsView, isHydrated }}>
      {children}
    </CarbonContext.Provider>
  );
}

export function useCarbonData() {
  const context = useContext(CarbonContext);
  if (context === undefined) {
    throw new Error("useCarbonData must be used within a CarbonDataProvider");
  }
  return context;
}
