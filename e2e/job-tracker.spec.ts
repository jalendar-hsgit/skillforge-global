import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:3000';

test.describe('Job Tracker', () => {
  test('Dashboard loads and shows stats and actions', async ({ page }) => {
    await page.goto(`${BASE_URL}/job-tracker`);

    await expect(page.getByRole('heading', { name: 'Job Application Tracker' })).toBeVisible();

    // Stats cards exist (at least one of the labels)
    await expect(page.getByText('Job Tracker')).toBeVisible({ timeout: 15000 });
    const totalApps = page.getByTestId('stat-total-applications')
    await Promise.race([
      totalApps.waitFor({ state: 'visible' }),
      page.getByText('Total Applications').waitFor({ state: 'visible' })
    ])

    // Add Application button navigates
    await page.getByRole('button', { name: 'Add Application' }).click();
    await expect(page).toHaveURL(/\/job-tracker\/add/);

    // Back to dashboard
    await page.goto(`${BASE_URL}/job-tracker`);

    // Settings link navigates
    await page.getByRole('button', { name: 'Settings' }).click();
    await expect(page).toHaveURL(/\/job-tracker\/settings/);
  });

  test('Kanban view toggles and renders columns', async ({ page }) => {
    await page.goto(`${BASE_URL}/job-tracker`);
    await page.getByRole('button', { name: 'Kanban' }).click();
    // Columns badges
    await expect(page.getByText('⭐ Wishlist')).toBeVisible();
    await expect(page.getByText('📨 Applied')).toBeVisible();
  });
});
