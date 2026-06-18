import React from 'react';

export const SIMULATOR_SCENARIOS = [
  {
    name: "Switch to 100% Renewable Tariff",
    subtitle: "Zero-carbon electricity for your home",
    icon: <svg className="w-6 h-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>,
    params: { type: "add_renewable", switch_to_renewable_tariff: true, add_solar_panels: false }
  },
  {
    name: "Install Rooftop Solar",
    subtitle: "Generate your own clean energy",
    icon: <svg className="w-6 h-6 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>,
    params: { type: "add_renewable", switch_to_renewable_tariff: true, add_solar_panels: true, upfront_cost_usd: 15000 }
  },
  {
    name: "Adopt a Vegan Diet",
    subtitle: "Plant-based eating for maximum impact",
    icon: <svg className="w-6 h-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>,
    params: { type: "switch_diet", new_diet: "vegan" }
  },
  {
    name: "Switch to Electric Vehicle",
    subtitle: "Zero-tailpipe emissions driving",
    icon: <svg className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>,
    params: { type: "switch_car", new_car_type: "electric", upfront_cost_usd: 35000 }
  }
];
