"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import { CarbonProfile, CarbonInventory } from "@/types/carbon";
import { useLocalStorage } from "@/hooks/useLocalStorage";
import { useRankedActions } from "@/hooks/useRankedActions";
import { OcrDataSchema } from "@/types/schemas";

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
  inventory: CarbonInventory;
  profile: CarbonProfile;
  individual_results?: (OcrData & { filename: string })[];
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
  const {
    storedValue: ocrData,
    setValue: setOcrData,
    isHydrated,
  } = useLocalStorage<OcrData>("carbonpilot_ocr_data", null, (val) => {
    const result = OcrDataSchema.safeParse(val);
    if (result.success) return result.data as OcrData;
    console.warn("Invalid OCR data found in localStorage:", result.error);
    return null;
  });
  const [actionsView, setActionsView] = useState<"combined" | number>(
    "combined",
  );

  const { actions, loadingActions } = useRankedActions(
    ocrData,
    actionsView,
    isHydrated,
  );

  return (
    <CarbonContext.Provider
      value={{
        ocrData,
        setOcrData,
        actions,
        loadingActions,
        actionsView,
        setActionsView,
        isHydrated,
      }}
    >
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
