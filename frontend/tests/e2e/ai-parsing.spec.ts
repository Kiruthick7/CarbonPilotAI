import { test, expect } from '@playwright/test';

test.describe('Flow 5 - AI Scenario Parsing', () => {
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

  test('User can query multiple scenarios using natural language', async ({ page }) => {
    
    await page.route('http://127.0.0.1:8000/v1/simulate/ai', async route => {
      const json = {
        original_total: 6.0,
        new_total: 3.7,
        delta_co2e: -2.3,
        delta_percent: -35.0,
        new_inventory: {
          total_tco2e: 3.7,
          breakdowns: []
        },
        upfront_cost_usd: 35000,
        annual_saving_usd: 1700,
        years_to_break_even: 20.5,
        applied_scenarios: ["Switch to EV", "Vegan Diet"],
        co_benefits: []
      };
      await route.fulfill({ json });
    });

    
    await page.goto('/simulator');

    
    const input = page.getByPlaceholder(/Switch to an EV/i);
    await input.fill("What if I buy an EV and switch to a vegan diet?");

    
    await page.keyboard.press('Enter');

    
    await expect(page.locator('text=-2.30')).toBeVisible(); 
    await expect(page.locator('text=35.0%')).toBeVisible(); 
  });
});
