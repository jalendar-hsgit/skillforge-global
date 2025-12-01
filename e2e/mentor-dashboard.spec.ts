import { test, expect } from '@playwright/test'

test('mentor dashboard loads sessions', async ({ page }) => {
  await page.goto('/login')
  await page.fill('input[type="email"]', 'mentor@test.com')
  await page.fill('input[type="password"]', 'password123')
  await page.click('button[type="submit"]')
  await page.waitForURL(/dashboard|mentors\/dashboard/)

  await page.goto('/mentors/dashboard')
  await expect(page.getByText('Mentor Dashboard')).toBeVisible()
  // Assert the section heading specifically to avoid strict mode conflicts
  await expect(page.getByRole('heading', { name: /Upcoming Sessions/i })).toBeVisible()
})
