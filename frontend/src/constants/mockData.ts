import { OcrData } from "@/context/CarbonDataContext";

export const DEMO_CARBON_PROFILE_DATA: OcrData = {
  success: true,
  filename: "sample_bill.pdf",
  kwh_usage: 450.0,
  total_cost_usd: 135.0,
  confidence: 1.0,
  calculated_footprint_tco2e: 0.173,
  profile: {
    country_code: "US",
    home: {
      home_size: "medium",
      heating_type: "gas",
      num_occupants: 2,
      has_solar: false,
      renewable_tariff: false,
    },
  },
  inventory: {
    total_tco2e: 7.72,
    breakdowns: [
      {
        category: "transport",
        total_kgco2e: 1820.0,
        subcategories: [
          { label: "Car", kgco2e: 1820.0, share_of_category: 1.0 },
          { label: "Short-haul flights", kgco2e: 0.0, share_of_category: 0.0 },
          { label: "Long-haul flights", kgco2e: 0.0, share_of_category: 0.0 },
          { label: "Public transport", kgco2e: 0.0, share_of_category: 0.0 },
        ],
      },
      {
        category: "diet",
        total_kgco2e: 2310.0,
        subcategories: [
          { label: "Food production", kgco2e: 2310.0, share_of_category: 1.0 },
          { label: "Food waste", kgco2e: 0.0, share_of_category: 0.0 },
        ],
      },
      {
        category: "home",
        total_kgco2e: 2450.0,
        subcategories: [
          { label: "Heating", kgco2e: 0.0, share_of_category: 0.0 },
          { label: "Electricity", kgco2e: 2450.0, share_of_category: 1.0 },
        ],
      },
      {
        category: "consumption",
        total_kgco2e: 1140.0,
        subcategories: [
          { label: "Clothing", kgco2e: 1140.0, share_of_category: 1.0 },
          { label: "Electronics", kgco2e: 0.0, share_of_category: 0.0 },
          { label: "Deliveries", kgco2e: 0.0, share_of_category: 0.0 },
        ],
      },
    ],
    national_average_tco2e: 4.8,
    global_average_tco2e: 4.8,
    budget_1_5c_tco2e: 2.3,
  },
};
