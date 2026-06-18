import { test, expect } from '@playwright/test';

test.describe('Flow 1 - OCR Upload Journey', () => {
  test('User can upload utility bill and view dashboard', async ({ page }) => {

    await page.route('http://127.0.0.1:8000/v1/actions/rank', async route => {
      await route.fulfill({ json: { actions: [], total_achievable_reduction: 0 } });
    });


    await page.route('http://127.0.0.1:8000/v1/calculate', async route => {
      await route.fulfill({ json: { inventory: { total_tco2e: 7.88, breakdowns: [{ category: "digital", total_kgco2e: 160 }] } } });
    });

    
    await page.route('http://127.0.0.1:8000/v1/ocr/upload', async route => {
      const json = {
        results: [
          {
            parsed_data: {
              kwh_usage: 450,
              total_cost: 135.0,
              confidence: 1.0,
              parsed_footprints: {
                home: 2.45,
                transport: 1.82,
                diet: 2.31,
                consumption: 1.14
              }
            },
            filename: 'sample_bill.pdf',
            error: null
          }
        ],
        calculated_footprint_tco2e: 6.0,
        kwh_usage: 450,
        filename: "bill.pdf",
        total_cost_usd: 120,
        confidence: 0.95,
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
      };
      await route.fulfill({ json });
    });

    
    await page.goto('/onboarding');
    
    
    const filePayload = Buffer.from('dummy pdf content');
    
    
    
    const fileInput = page.locator('input[type="file"]');
    
    
    await fileInput.setInputFiles({
      name: 'sample_bill.pdf',
      mimeType: 'application/pdf',
      buffer: filePayload,
    });
    
    
    await page.check('input#privacy-consent');

    
    
    await page.click('button:has-text("Process & Continue")');
    await page.click('button:has-text("Finish & View Dashboard")');

    
    
    await page.waitForURL('**/dashboard');
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    
    
    
    await expect(page.getByText(/home/i).first()).toBeVisible();
    await expect(page.locator('text=2.45 tCO₂e')).toBeVisible();
    
    
    await expect(page.locator('text=Total Baseline Footprint')).toBeVisible();
    await expect(page.getByText('450 kWh', { exact: true })).toBeVisible();
  });
});
