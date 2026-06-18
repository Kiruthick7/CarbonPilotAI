import { test, expect } from '@playwright/test';

test.describe('Flow 3 - Recommendation Engine', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/v1/actions/rank', async route => {
      await route.fulfill({ json: { actions: [], total_achievable_reduction: 0 } }).catch(() => {});
    });

    
    await page.addInitScript(() => {
      window.localStorage.setItem('carbonpilot_ocr_data', JSON.stringify({
        calculated_footprint_tco2e: 6.0,
        profile: {
          kwh_usage: 450,
          heating_type: "GAS",
          diet_type: "AVERAGE"
        },
        inventory: {
          total_tco2e: 7.72,
          breakdowns: [
            { category: "home", total_kgco2e: 2450 },
            { category: "transport", total_kgco2e: 1820 },
            { category: "diet", total_kgco2e: 2310 },
            { category: "consumption", total_kgco2e: 1140 }
          ]
        }
      }));
    });
  });

  test('Dashboard loads recommendations and sorted correctly', async ({ page }) => {
    
    await page.route('http://127.0.0.1:8000/v1/actions/rank', async route => {
      const json = {
        actions: [
          {
            id: "ev", 
            title: "Switch to Electric Vehicle", 
            description: "Buy an EV",
            category: "transport",
            co2e_saved_per_year: 2.1,
            effort_score: 3,
            impact_score: 5,
            composite_score: 9.5,
            upfront_cost_usd: 40000,
            annual_saving_usd: 1200,
            time_to_impact_days: 30,
            co_benefits: [],
            why_recommended: "Because you drive a lot.",
            is_feasible: true
          },
          {
            id: "led", 
            title: "Switch to LED Lighting", 
            description: "Buy LEDs",
            category: "home",
            co2e_saved_per_year: 0.5,
            effort_score: 1,
            impact_score: 2,
            composite_score: 8.5,
            upfront_cost_usd: 100,
            annual_saving_usd: 50,
            time_to_impact_days: 1,
            co_benefits: [],
            why_recommended: "Quick win.",
            is_feasible: true
          }
        ],
        total_achievable_reduction: 2.6
      };
      await route.fulfill({ json });
    });

    
    await page.goto('/actions');

    
    await expect(page.locator('text=Switch to Electric Vehicle')).toBeVisible();
    await expect(page.locator('text=Switch to LED Lighting')).toBeVisible();

    
    await expect(page.locator('text=2.10 tCO₂e')).toBeVisible();

    
    const titles = await page.locator('h3').allTextContents();
    
    const evIndex = titles.findIndex(t => t === 'Switch to Electric Vehicle');
    const ledIndex = titles.findIndex(t => t === 'Switch to LED Lighting');
    
    expect(evIndex).toBeLessThan(ledIndex);
  });
});
