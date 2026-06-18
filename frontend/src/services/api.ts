import { CarbonProfile, CarbonInventory } from "@/types/carbon";

const getApiUrl = () =>
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/v1";

export const carbonApi = {
  uploadUtilityBills: async (files: File[]) => {
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));

    const response = await fetch(`${getApiUrl()}/ocr/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Failed to process document locally.");
    return response.json();
  },

  submitManualEntry: async (kwh: number) => {
    const response = await fetch(`${getApiUrl()}/ocr/manual`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kwh_usage: kwh }),
    });

    if (!response.ok) throw new Error("Failed to process manual entry.");
    return response.json();
  },

  calculateDigitalFootprint: async (profile: CarbonProfile) => {
    const response = await fetch(`${getApiUrl()}/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile),
    });

    if (!response.ok) throw new Error("Failed to process digital footprint.");
    return response.json();
  },

  fetchRankedActions: async (
    inventory: CarbonInventory,
    profile: CarbonProfile,
    constraints: Record<string, unknown> = {},
  ) => {
    const response = await fetch(`${getApiUrl()}/actions/rank`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ inventory, profile, constraints }),
    });

    if (!response.ok) throw new Error("Failed to rank actions.");
    return response.json();
  },
};
