import { test, expect } from '@playwright/test';

test.describe('Flow 2 - Manual Entry Journey', () => {
  test('User can manually enter kWh and see dashboard', async ({ page }) => {
    
    await page.goto('/onboarding');
    
    
    await page.click('button:has-text("Enter Manually")');
    
    
    const input = page.locator('input[type="number"]');
    await expect(input).toBeVisible();
    await input.fill('450');
    
    
    await page.click('button:has-text("Generate Carbon Profile")');
    
    
    await page.waitForURL('**/dashboard');
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    
    await expect(page.locator('text=Utility Bill Data')).toBeVisible();
    await expect(page.getByText('450 kWh', { exact: true })).toBeVisible();
    await expect(page.locator('text=Total Baseline Footprint')).toBeVisible();
  });
});
