import { test, expect } from '@playwright/test'

const BASE_URL = 'http://localhost:3000'

async function login(page) {
  await page.goto(`${BASE_URL}/login`)
  await page.fill('input[type="email"]', 'mentor@test.com')
  await page.fill('input[type="password"]', 'password123')
  await page.click('button[type="submit"]')
  await page.waitForURL(/dashboard|mentors\/dashboard/)
}

test('mentor dashboard loads sessions', async ({ page }) => {
  await login(page)
  await page.goto(`${BASE_URL}/mentors/dashboard`)
  await expect(page.getByText('Mentor Dashboard')).toBeVisible()
  await expect(page.getByText('Upcoming Sessions')).toBeVisible()
})
