import { test, expect, request } from '@playwright/test'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

// Detect Next.js port dynamically (3000-3003)
const FRONTEND_PORT = process.env.E2E_FRONTEND_PORT || '3000'
const APP = `http://127.0.0.1:${FRONTEND_PORT}`

function uniqueEmail() {
  const ts = Date.now()
  return `e2e_import_${ts}@example.com`
}

async function createPdfBufferWithText(text: string): Promise<Buffer> {
  // Generate a simple PDF with the provided text using pdfkit
  const PDFDocument = (await import('pdfkit')).default as any
  const doc = new PDFDocument({ size: 'A4', margin: 50 })
  const chunks: Buffer[] = []
  return await new Promise<Buffer>((resolve, reject) => {
    doc.on('data', (chunk: Buffer) => chunks.push(chunk))
    doc.on('end', () => resolve(Buffer.concat(chunks)))
    doc.on('error', reject)

    doc.fontSize(18).text('Resume Import E2E', { align: 'left' })
    doc.moveDown()
    doc.fontSize(12).text(text, { align: 'left' })
    doc.end()
  })
}

async function loginViaNextApi(baseUrl: string, email: string, password: string, pageContext: any) {
  // Sign up
  const signup = await pageContext.post(`${baseUrl}/api/session/signup`, {
    data: { email, password, full_name: 'E2E Import User' },
  })
  expect(signup.ok()).toBeTruthy()

  // Return without logging in here; we'll log in via browser context to ensure cookies are set
}

// Helper to save a buffer to a temp file (not strictly needed for setInputFiles object form, but handy for debugging)
function writeTempFile(buffer: Buffer, name: string): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sfg-import-'))
  const filePath = path.join(dir, name)
  fs.writeFileSync(filePath, buffer)
  return filePath
}

test.describe('Resume Import flow (PDF)', () => {
  test('upload -> parse preview -> import -> editor', async ({ page, request: api, context }) => {
    // Prepare account
    const email = uniqueEmail()
    const password = 'Test1234!'

    // Use a separate API context for auth calls
    const apiCtx = await request.newContext()
    await loginViaNextApi(APP, email, password, apiCtx)

    // Log in via browser context so HttpOnly cookie is set for this page context
    await page.goto(APP, { waitUntil: 'domcontentloaded' }).catch(() => {})
    const loginResp = await page.evaluate(async ({ email, password }) => {
      const r = await fetch('/api/session/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include',
      })
      return { ok: r.ok, status: r.status }
    }, { email, password })

    expect(loginResp.ok).toBeTruthy()

    // Sanity check auth via browser
    const meResp = await page.evaluate(async () => {
      const r = await fetch('/api/session/me', { credentials: 'include' })
      return { ok: r.ok, status: r.status }
    })
    expect(meResp.ok).toBeTruthy()

    // Navigate to import page
    await page.goto(`${APP}/resumes/import`, { waitUntil: 'domcontentloaded' })

    // Generate a small PDF with recognizable resume-like text
    const pdfText = [
      'John Doe',
      'john@example.com',
      '555-555-1234',
      'Professional Summary',
      'Experienced developer with a focus on building robust web applications.'
    ].join('\n')

    const pdfBuffer = await createPdfBufferWithText(pdfText)

    // Upload the PDF via the hidden file input
    const fileChooser = page.locator('input[type="file"][id="resume-file"]')
    await expect(fileChooser).toBeVisible()

    await fileChooser.setInputFiles({
      name: 'sample-resume.pdf',
      mimeType: 'application/pdf',
      buffer: pdfBuffer,
    })

    // Click Parse Resume button
    // Ensure network is idle and form is ready
    await page.waitForLoadState('networkidle')
    await expect(page.getByRole('button', { name: /Parse Resume/i })).toBeEnabled({ timeout: 10000 })

    // Click Parse Resume and wait for either preview response or preview UI
    const parsePromise = page.waitForResponse(r => r.url().includes('/api/session/v1x/resume-import/parse-preview'), { timeout: 30000 })
    await page.getByRole('button', { name: /Parse Resume/i }).click()
    let parseResp: any
    try {
      parseResp = await parsePromise
    } catch (e) {
      // Fallback: some deployments render preview without network call; wait for preview UI
      await page.waitForSelector('[data-testid="import-preview"]', { timeout: 15000 })
    }
    const parseBody = parseResp ? await parseResp.text() : '{}'
    console.log('parse-preview status', parseResp.status(), 'body', parseBody)
    expect(parseResp.ok(), `parse-preview failed ${parseResp.status()} body: ${parseBody}`).toBeTruthy()

    // Expect parse success indicator
    await expect(page.getByText(/Resume parsed successfully/i)).toBeVisible({ timeout: 20000 })

    // Basic assertions for extracted fields labels
    await expect(page.getByText(/Name/i)).toBeVisible()
    await expect(page.getByText(/Email/i)).toBeVisible()
    await expect(page.getByText(/Phone/i)).toBeVisible()

    // Import resume
    await page.getByRole('button', { name: /Import Resume/i }).click()

    // After import, the modal should close and we should land on the editor for the new resume
    // Wait for navigation to an editor URL and editor UI to appear
    await expect.poll(async () => page.url(), { timeout: 20000, intervals: [250, 500, 750, 1000] }).toMatch(/\/resumes\/\d+\/edit/i)

    await expect(page.getByRole('heading', { name: /Live Preview/i })).toBeVisible({ timeout: 25000 })
  })
})
