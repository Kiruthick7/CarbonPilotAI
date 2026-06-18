import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Flow 6 - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    
    await page.addInitScript(() => {
      window.localStorage.setItem('carbonpilot_ocr_data', JSON.stringify({
        calculated_footprint_tco2e: 6.0,
        kwh_usage: 450,
        filename: "bill.pdf",
        total_cost_usd: 120,
        confidence: 0.95,
        profile: { kwh_usage: 450, heating_type: "GAS", diet_type: "AVERAGE" },
        inventory: {
          total_tco2e: 7.72,
          breakdowns: [
            { category: "home", total_kgco2e: 2450 },
            { category: "transport", total_kgco2e: 1820 }
          ]
        }
      }));
    });
  });

  test('Onboarding page should not have any automatically detectable accessibility issues', async ({ page }) => {
    await page.goto('/onboarding');
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .disableRules(['color-contrast'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('Dashboard page should not have any automatically detectable accessibility issues', async ({ page }) => {
    await page.goto('/dashboard');
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .disableRules(['color-contrast'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });
  
  test('Actions/Ranking page should not have any automatically detectable accessibility issues', async ({ page }) => {
    
    await page.route('http://127.0.0.1:8000/v1/actions/rank', async route => {
      await route.fulfill({ json: { ranked_actions: [], total_potential_reduction_tco2e: 0 } });
    });
    
    await page.goto('/actions');
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .disableRules(['color-contrast'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
