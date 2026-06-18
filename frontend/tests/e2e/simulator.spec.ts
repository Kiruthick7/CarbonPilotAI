import { test, expect } from '@playwright/test';

test.describe('Flow 4 - Simulator', () => {
  test.beforeEach(async ({ page }) => {
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

  test('User can select EV scenario and run simulation', async ({ page }) => {
    await page.route('http://127.0.0.1:8000/v1/simulate', async route => {
      const json = {
        original_total: 6.0,
        new_total: 4.5,
        delta_co2e: -1.5,
        delta_percent: -25.0,
        new_inventory: {
          total_tco2e: 4.5,
          breakdowns: []
        },
        upfront_cost_usd: 35000,
        annual_saving_usd: 1200,
        years_to_break_even: 29.1,
        applied_scenarios: ["Switch to Electric Vehicle"],
        co_benefits: []
      };
      await route.fulfill({ json });
    });

    await page.goto('/simulator');

    await page.getByText('Switch to Electric Vehicle').click();

    await expect(page.locator('text=-1.50')).toBeVisible();
  });
});
