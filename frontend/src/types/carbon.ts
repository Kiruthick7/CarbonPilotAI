export interface CarbonProfile {
  country_code?: string;
  transport?: {
    car?: { car_type: string; weekly_km: number; };
    flights?: { short_haul_flights: number; long_haul_flights: number; };
    weekly_public_transport_km?: number;
    public_transport_split_bus?: number;
  };
  home?: {
    home_size: string;
    heating_type: string;
    num_occupants: number;
    has_solar?: boolean;
    renewable_tariff?: boolean;
  };
  diet?: {
    diet_type: string;
    food_waste: string;
  };
  consumption?: {
    new_clothing_items_per_year: number;
    new_electronics_per_year: number;
    online_deliveries_per_week: number;
  };
  digital?: {
    device_upgrade_frequency: string;
    streaming_gaming_usage: string;
    ai_cloud_usage: string;
  };
  [key: string]: unknown;
}

export interface SubcategoryItem {
  label: string;
  kgco2e: number;
}

export interface CategoryBreakdown {
  category: string;
  total_kgco2e: number;
  subcategories?: SubcategoryItem[];
  [key: string]: unknown;
}

export interface CarbonInventory {
  total_tco2e: number;
  breakdowns: CategoryBreakdown[];
  trace?: {
    formula: string;
    variables: Record<string, string>;
    source: string;
  };
  [key: string]: unknown;
}
