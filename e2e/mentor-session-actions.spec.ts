import { test, expect } from '@playwright/test'
import { loginOnce } from './helpers/auth'

const BACKEND_BASE = 'http://127.0.0.1:8001';
const FRONTEND_BASE = 'http://localhost:3000';

// Helper to login as mentor via backend and inject cookie
async function loginAsMentor(page: any, context: any) {
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
}

// Helper to create a test session via API
async function createTestSession(page: any, status: string = 'pending') {
  const response = await page.request.post('http://localhost:8001/api/v1x/mentors/sessions', {
    data: {
      student_id: 1,
      topic: `E2E Test Session - ${status}`,
      description: 'Created by E2E test',
      scheduled_at: new Date(Date.now() + 86400000).toISOString(), // Tomorrow
      duration_minutes: 60
    }
  })
  expect(response.ok()).toBeTruthy()
  return await response.json()
}

test.describe('Mentor Session Actions', () => {
  test.beforeEach(async ({ page, context }) => {
    // Ensure authenticated context using shared helper to reduce rate limits
    await loginOnce(context, context.request, 'mentor-e2e@skillforge.com', 'Test1234!', 'Mentor E2E')
    await loginAsMentor(page, context)
  })

  test('displays pending sessions with confirm button', async ({ page }) => {
    await page.goto('/mentors/dashboard/sessions')
    
    // Check for sessions heading
    await expect(page.getByRole('heading', { name: /My Sessions/i })).toBeVisible()
    
    // Look for pending sessions
    const pendingBadge = page.locator('[data-status="pending"]').first()
    if (await pendingBadge.count() > 0) {
      await expect(pendingBadge).toBeVisible()
      
      // Find confirm button associated with pending session
      const sessionRow = pendingBadge.locator('..').locator('..')
      await expect(sessionRow.getByRole('button', { name: /confirm/i })).toBeVisible()
    }
  })

  test('confirms a pending session and generates meeting URL', async ({ page }) => {
    await page.goto('/mentors/dashboard/sessions')
    
    // Find first pending session
    const pendingSession = page.locator('[data-status="pending"]').first()
    
    if (await pendingSession.count() > 0) {
      const sessionRow = pendingSession.locator('..').locator('..')
      const sessionTopic = await sessionRow.locator('[data-testid="session-topic"]').textContent()
      
      // Click confirm button
      await sessionRow.getByRole('button', { name: /confirm/i }).click()
      
      // Wait for confirmation (could be modal or inline)
      await page.waitForTimeout(500)
      
      // Verify status changed to confirmed
      await expect(sessionRow.locator('[data-status="confirmed"]')).toBeVisible()
      
      // Verify meeting URL appears
      const meetingLink = sessionRow.getByRole('link', { name: /join meeting|meeting url/i })
      await expect(meetingLink).toBeVisible()
      
      // Verify meeting link is valid
      const href = await meetingLink.getAttribute('href')
      expect(href).toBeTruthy()
      expect(href).toMatch(/http/)
    } else {
      test.skip()
    }
  })

  test('completes a confirmed session', async ({ page }) => {
    await page.goto('/mentors/dashboard/sessions')
    
    // Find first confirmed session
    const confirmedSession = page.locator('[data-status="confirmed"]').first()
    
    if (await confirmedSession.count() > 0) {
      const sessionRow = confirmedSession.locator('..').locator('..')
      
      // Click complete button
      await sessionRow.getByRole('button', { name: /complete/i }).click()
      
      // Handle potential confirmation modal
      const confirmButton = page.getByRole('button', { name: /yes|confirm/i })
      if (await confirmButton.count() > 0) {
        await confirmButton.click()
      }
      
      await page.waitForTimeout(500)
      
      // Verify status changed to completed
      await expect(sessionRow.locator('[data-status="completed"]')).toBeVisible()
      
      // Verify complete button is no longer visible
      await expect(sessionRow.getByRole('button', { name: /complete/i })).not.toBeVisible()
    } else {
      test.skip()
    }
  })

  test('cancels a pending session with reason', async ({ page }) => {
    await page.goto('/mentors/dashboard/sessions')
    
    // Find first pending or confirmed session
    const cancellableSession = page.locator('[data-status="pending"], [data-status="confirmed"]').first()
    
    if (await cancellableSession.count() > 0) {
      const sessionRow = cancellableSession.locator('..').locator('..')
      
      // Click cancel button
      await sessionRow.getByRole('button', { name: /cancel/i }).click()
      
      // Fill in cancellation reason (if modal appears)
      const reasonInput = page.getByLabel(/reason|note/i)
      if (await reasonInput.count() > 0) {
        await reasonInput.fill('E2E test cancellation - scheduling conflict')
        await page.getByRole('button', { name: /confirm cancel|yes/i }).click()
      }
      
      await page.waitForTimeout(500)
      
      // Verify status changed to cancelled
      await expect(sessionRow.locator('[data-status="cancelled"]')).toBeVisible()
    } else {
      test.skip()
    }
  })

  test('filters sessions by status', async ({ page }) => {
    await page.goto('/mentors/dashboard/sessions')
    
    // Click on filter tabs/buttons
    const pendingFilter = page.getByRole('button', { name: /pending/i })
    if (await pendingFilter.count() > 0) {
      await pendingFilter.click()
      
      // Verify only pending sessions are shown
      const pendingItems = page.locator('[data-status="pending"]')
      const completedItems = page.locator('[data-status="completed"]')
      await expect(pendingItems.first()).toBeVisible({ timeout: 15000 })
      await expect(completedItems).toHaveCount(0)
    }
    
    const completedFilter = page.getByRole('button', { name: /completed/i })
    if (await completedFilter.count() > 0) {
      await completedFilter.click()
      
      // Verify only completed sessions are shown
      await expect(page.locator('[data-status="completed"]')).toBeVisible()
      await expect(page.locator('[data-status="pending"]')).not.toBeVisible()
    }
  })

  test('displays session details in modal', async ({ page }) => {
    await page.goto('/mentors/dashboard/sessions')
    
    const firstSession = page.locator('[data-testid="session-row"]').first()
    
    if (await firstSession.count() > 0) {
      // Click to open details
      await firstSession.click()
      
      // Verify modal/details panel appears
      const modal = page.locator('[role="dialog"], [data-testid="session-modal"]')
      await expect(modal).toBeVisible()
      
      // Verify key details are present
      await expect(modal.getByText(/topic/i)).toBeVisible()
      await expect(modal.getByText(/student/i)).toBeVisible()
      await expect(modal.getByText(/scheduled/i)).toBeVisible()
      await expect(modal.getByText(/duration/i)).toBeVisible()
      
      // Close modal
      await modal.getByRole('button', { name: /close/i }).click()
      await expect(modal).not.toBeVisible()
    } else {
      test.skip()
    }
  })

  test('shows meeting URL only after confirmation', async ({ page }) => {
    await page.goto('/mentors/dashboard/sessions')
    
    // Check pending session doesn't have meeting URL
    const pendingSession = page.locator('[data-status="pending"]').first()
    if (await pendingSession.count() > 0) {
      const sessionRow = pendingSession.locator('..').locator('..')
      await expect(sessionRow.getByRole('link', { name: /join meeting/i })).not.toBeVisible()
    }
    
    // Check confirmed session does have meeting URL
    const confirmedSession = page.locator('[data-status="confirmed"]').first()
    if (await confirmedSession.count() > 0) {
      const sessionRow = confirmedSession.locator('..').locator('..')
      await expect(sessionRow.getByRole('link', { name: /join meeting/i })).toBeVisible()
    }
  })

  test('updates dashboard stats after session completion', async ({ page }) => {
    // Go to dashboard and record current stats
    await page.goto('/mentors/dashboard')
    await page.waitForLoadState('networkidle')
    const completedStat = page.getByTestId('stat-completed')
    const completedCountText = (await completedStat.textContent()) || (await page.getByText(/completed/i).first().textContent())
    const currentCompleted = parseInt(completedCountText?.match(/\d+/)?.[0] || '0')
    
    // Complete a session
    await page.goto('/mentors/dashboard/sessions')
    const confirmedSession = page.locator('[data-status="confirmed"]').first()
    
    if (await confirmedSession.count() > 0) {
      const sessionRow = confirmedSession.locator('..').locator('..')
      await sessionRow.getByRole('button', { name: /complete/i }).click()
      
      const confirmButton = page.getByRole('button', { name: /yes|confirm/i })
      if (await confirmButton.count() > 0) {
        await confirmButton.click()
      }
      
      // Return to dashboard
      await page.goto('/mentors/dashboard')
      await page.waitForTimeout(1000)
      
      // Verify completed count increased
      const newCompletedText = await page.getByText(/completed/i).first().textContent()
      const newCompleted = parseInt(newCompletedText?.match(/\d+/)?.[0] || '0')
      expect(newCompleted).toBeGreaterThan(currentCompleted)
    } else {
      test.skip()
    }
  })

  test('prevents completing a pending session', async ({ page }) => {
    await page.goto('/mentors/dashboard/sessions')
    
    const pendingSession = page.locator('[data-status="pending"]').first()
    
    if (await pendingSession.count() > 0) {
      const sessionRow = pendingSession.locator('..').locator('..')
      
      // Complete button should not be available for pending sessions
      await expect(sessionRow.getByRole('button', { name: /^complete$/i })).not.toBeVisible()
    } else {
      test.skip()
    }
  })

  test('shows appropriate actions based on session status', async ({ page }) => {
    await page.goto('/mentors/dashboard/sessions')
    
    // Pending: should have Confirm and Cancel
    const pendingSession = page.locator('[data-status="pending"]').first()
    if (await pendingSession.count() > 0) {
      const row = pendingSession.locator('..').locator('..')
      await expect(row.getByRole('button', { name: /confirm/i })).toBeVisible()
      await expect(row.getByRole('button', { name: /cancel/i })).toBeVisible()
      await expect(row.getByRole('button', { name: /^complete$/i })).not.toBeVisible()
    }
    
    // Confirmed: should have Complete and Cancel
    const confirmedSession = page.locator('[data-status="confirmed"]').first()
    if (await confirmedSession.count() > 0) {
      const row = confirmedSession.locator('..').locator('..')
      await expect(row.getByRole('button', { name: /complete/i })).toBeVisible()
      await expect(row.getByRole('button', { name: /cancel/i })).toBeVisible()
      await expect(row.getByRole('button', { name: /confirm/i })).not.toBeVisible()
    }
    
    // Completed: should have no action buttons
    const completedSession = page.locator('[data-status="completed"]').first()
    if (await completedSession.count() > 0) {
      const row = completedSession.locator('..').locator('..')
      await expect(row.getByRole('button', { name: /confirm/i })).not.toBeVisible()
      await expect(row.getByRole('button', { name: /complete/i })).not.toBeVisible()
      await expect(row.getByRole('button', { name: /cancel/i })).not.toBeVisible()
    }
  })
})
