import { test, expect, request, Page, APIRequestContext } from '@playwright/test'

const APP = process.env.APP_URL || 'http://localhost:3000'

async function signupAndLogin(page: Page, api: APIRequestContext) {
  const email = `e2e_${Date.now()}@example.com`
  const password = 'Test1234!'
  await api.post(`${APP}/api/session/signup`, { data: { email, password } })
  const ctx = await request.newContext()
  const login = await ctx.post(`${APP}/api/session/login`, { data: { email, password } })
  expect(login.ok()).toBeTruthy()
  // ensure page context is alive and add cookies
  await page.goto(APP, { waitUntil: 'domcontentloaded' }).catch(() => {})
  const cookies = await ctx.storageState()
  await page.context().addCookies((cookies.cookies || []).map((c: any) => (c.domain ? c : { ...c, url: APP })))
}

test('Editor autosave updates Last saved after title change', async ({ page, request: api }) => {
  await signupAndLogin(page, api)

  // Create new resume (page handles creation on load)
  await page.goto(`${APP}/resumes/new`, { waitUntil: 'domcontentloaded' }).catch(() => {})

  // Wait for creation network call to complete
  await page.waitForResponse(r => r.url().includes('/api/session/resumes') && r.request().method() === 'POST' && r.ok(), { timeout: 20000 })

  // Change title and wait for PATCH debounce + network
  const title = page.getByTestId('input-title')
  await expect(title).toBeVisible()
  const newTitle = `E2E Title ${Date.now()}`
  await title.fill(newTitle)

  // Wait for PATCH to resumes with id query
  await page.waitForResponse(r => r.url().includes('/api/session/resumes?id=') && r.request().method() === 'PATCH' && r.ok(), { timeout: 30000 })

  // Expect Last saved indicator to appear
  await expect(page.getByTestId('status-save')).toContainText(/Last saved/i, { timeout: 20000 })
})
