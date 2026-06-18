import { useState, useEffect } from "react";
import { carbonApi } from "@/services/api";
import { OcrData, RankedAction } from "@/context/CarbonDataContext";

export function useRankedActions(
  ocrData: OcrData | null,
  actionsView: "combined" | number,
  isHydrated: boolean,
) {
  const [actions, setActions] = useState<RankedAction[]>([]);
  const [loadingActions, setLoadingActions] = useState(false);

  useEffect(() => {
    async function fetchActions() {
      if (!ocrData || !ocrData.inventory || !ocrData.profile) {
        setActions([]);
        return;
      }

      setLoadingActions(true);
      try {
        const currentData =
          actionsView === "combined"
            ? ocrData
            : ocrData.individual_results?.[actionsView as number] || ocrData;

        if (!currentData.inventory || !currentData.profile) {
          setActions([]);
          setLoadingActions(false);
          return;
        }

        const result = await carbonApi.fetchRankedActions(
          currentData.inventory,
          currentData.profile,
          {},
        );

        setActions(result.actions || []);
      } catch (err) {
        console.error("Failed to fetch actions:", err);
        setActions([]);
      } finally {
        setLoadingActions(false);
      }
    }

    if (isHydrated) {
      fetchActions();
    }
  }, [ocrData, actionsView, isHydrated]);

  return { actions, loadingActions, setActions };
}
