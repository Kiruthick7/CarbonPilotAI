import { test, expect } from '@playwright/test';

test.describe('Flow 2 - Manual Entry Journey', () => {
  test('User can manually enter kWh and see dashboard', async ({ page }) => {

    await page.route('http://127.0.0.1:8000/v1/ocr/manual', async route => {
      await route.fulfill({ json: { success: true, kwh_usage: 450, filename: "Manual Entry", profile: { kwh_usage: 450 }, inventory: { total_tco2e: 7.72, breakdowns: [] } } });
    });


    await page.route('http://127.0.0.1:8000/v1/actions/rank', async route => {
      await route.fulfill({ json: { actions: [], total_achievable_reduction: 0 } });
    });


    await page.route('http://127.0.0.1:8000/v1/calculate', async route => {
      await route.fulfill({ json: { inventory: { total_tco2e: 7.88, breakdowns: [{ category: "digital", total_kgco2e: 160 }] } } });
    });

    
    await page.goto('/onboarding');
    
    
    await page.click('button:has-text("Enter Manually")');
    
    
    const input = page.locator('input[type="number"]');
    await expect(input).toBeVisible();
    await input.fill('450');
    
    
    
    await page.click('button:has-text("Generate Carbon Profile")');
    await page.click('button:has-text("Finish & View Dashboard")');

    
    
    await page.waitForURL('**/dashboard');
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    
    await expect(page.locator('text=Utility Bill Data')).toBeVisible();
    await expect(page.getByText('450 kWh', { exact: true })).toBeVisible();
    await expect(page.locator('text=Total Baseline Footprint')).toBeVisible();
  });
});
