import { test, expect } from '@playwright/test'
import { loginOnce } from './helpers/auth'

const BACKEND_BASE = 'http://127.0.0.1:8001';
const FRONTEND_BASE = 'http://localhost:3000';

test('mentor dashboard loads sessions', async ({ page, context, request }) => {
  await loginOnce(context, request, 'mentor-e2e@skillforge.com', 'Test1234!', 'Mentor E2E')
  // Backend login to avoid Next.js proxy rate limits
  const loginResp = await context.request.post(`${BACKEND_BASE}/api/v1/auth/login`, {
    data: { email: 'mentor@test.com', password: 'password123' }
  });
  const setCookie = loginResp.headers()['set-cookie'] as unknown as string | undefined;
  if (setCookie && setCookie.includes('token=')) {
    const tokenMatch = setCookie.match(/token=([^;]+)/);
    if (tokenMatch) {
      await context.addCookies([{
        name: 'token',
        value: tokenMatch[1],
        domain: 'localhost',
        path: '/',
        httpOnly: true,
        sameSite: 'Lax',
      }]);
    }
  }

  await page.goto('/mentors/dashboard')
  await expect(page.getByText('Mentor Dashboard')).toBeVisible({ timeout: 15000 })
  // Assert the section heading specifically to avoid strict mode conflicts; fallback to data-testid
  const upcomingHeading = page.getByRole('heading', { name: /Upcoming Sessions/i })
  const upcomingTestId = page.getByTestId('heading-upcoming-sessions')
  await Promise.race([
    upcomingHeading.waitFor({ state: 'visible' }),
    upcomingTestId.waitFor({ state: 'visible' })
  ])
})
