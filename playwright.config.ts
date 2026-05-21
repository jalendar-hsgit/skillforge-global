import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: 1,
  reporter: 'list',
  timeout: 60000, // Increase timeout for slower SSR renders
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // Wait for dev servers to be ready before running tests
  webServer: process.env.SKIP_WEBSERVER ? undefined : [
    {
      // Ensure backend deps are installed in CI before starting
      command: 'cd backend && python -m pip install -r requirements.txt && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001',
      port: 8001,
      timeout: 180000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run dev',
      port: 3000,
      timeout: 180000,
      env: {
        NEXT_PUBLIC_API_BASE: 'http://127.0.0.1:8001',
        API_BASE: 'http://127.0.0.1:8001',
      },
      reuseExistingServer: !process.env.CI,
    },
  ],
})
