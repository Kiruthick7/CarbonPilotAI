export interface CoBenefit {
  type: string;
  description: string;
}

export interface SimulationResult {
  delta_co2e: number;
  delta_percent: number;
  annual_saving_usd?: number;
  co_benefits: CoBenefit[];
  applied_scenarios?: string[];
  new_inventory?: {
    total_tco2e: number;
    trace?: {
      formula: string;
      variables: Record<string, string>;
      source: string;
    };
    breakdowns?: Array<{
      category: string;
      total_kgco2e: number;
    }>;
  };
}
