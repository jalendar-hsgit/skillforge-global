import { test, expect, request, Page, APIRequestContext } from '@playwright/test'

const APP = process.env.APP_URL || 'http://localhost:3000'

async function signupAndLogin(page: Page, api: APIRequestContext) {
  const email = `e2e_${Date.now()}@example.com`
  const password = 'Test1234!'
  await api.post(`${APP}/api/session/signup`, { data: { email, password } })
  const ctx = await request.newContext()
  const login = await ctx.post(`${APP}/api/session/login`, { data: { email, password } })
  expect(login.ok()).toBeTruthy()
  await page.goto(APP, { waitUntil: 'domcontentloaded' }).catch(() => {})
  const cookies = await ctx.storageState()
  await page.context().addCookies((cookies.cookies || []).map((c: any) => (c.domain ? c : { ...c, url: APP })))
}

test('AI suggestions render after clicking generate', async ({ page, request: api }) => {
  await signupAndLogin(page, api)
  await page.goto(`${APP}/resumes/new`, { waitUntil: 'domcontentloaded' }).catch(() => {})
  await page.waitForResponse(r => r.url().includes('/api/session/resumes') && r.request().method() === 'POST' && r.ok(), { timeout: 20000 })

  const button = page.getByTestId('btn-ai-generate')
  await expect(button).toBeVisible()
  await button.click()

  // Expect call to resume-ai endpoint and suggestions to render
  await page.waitForResponse(r => r.url().includes('/api/session/resume-ai/professional-summary') && r.request().method() === 'POST', { timeout: 30000 })
  await expect(page.getByTestId('ai-suggestions')).toBeVisible({ timeout: 30000 })
})
