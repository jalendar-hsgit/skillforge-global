import { test, expect, request } from '@playwright/test'

const APP = process.env.APP_URL || 'http://localhost:3000'

// helper to create a unique test user
function uniqueEmail() {
  const ts = Date.now()
  return `e2e_${ts}@example.com`
}

test.describe('Auth and Resume flow', () => {
  test('unauthenticated user is redirected to login, then resume is created after login', async ({ page, request }) => {
    // 1) Visit protected page and assert redirect client-side after load
    await page.goto(`${APP}/resumes/new`)

    // It might render briefly before redirect; wait for either Login header or redirect query
    await page.waitForURL(/\/login\?redirect=%2Fresumes%2Fnew|\/login\?redirect=\/resumes\/new/, { timeout: 15000 })
    expect(page.url()).toMatch(/\/login\?redirect=/)

    // 2) Create account via Next.js API
    const email = uniqueEmail()
    const password = 'Test1234!'
    const signup = await request.post(`${APP}/api/session/signup`, {
      data: { email, password, full_name: 'E2E User' },
    })
    expect(signup.ok()).toBeTruthy()

    // 3) Login via Next.js API to set session cookie on the same domain
    const ctx = await request.newContext()
    const login = await ctx.post(`${APP}/api/session/login`, {
      data: { email, password },
    })
    expect(login.ok()).toBeTruthy()

    // copy login cookies to page context
    const cookies = await ctx.storageState()
    await page.context().addCookies((cookies.cookies || []).map(c => ({ ...c, url: APP })))

    // 4) Now navigate again to protected page, should NOT redirect and should create resume
    await page.goto(`${APP}/resumes/new`)

    // Expect loading state then editor; the create is via proxy which returns id
    await expect(page.getByText(/Creating your resume|Loading/i)).toBeVisible({ timeout: 10000 })

    // After creation, a piece of the editor UI should appear; look for common heading or button from ResumeEditor
    await expect(page.getByText(/Live Preview|Export PDF|Work Experience/i)).toBeVisible({ timeout: 20000 })
  })
})
