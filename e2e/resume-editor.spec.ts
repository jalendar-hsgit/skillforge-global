import { test, expect } from '@playwright/test';

// Detect Next.js port dynamically
const FRONTEND_PORT = process.env.E2E_FRONTEND_PORT || '3000';
const FRONTEND_BASE = `http://127.0.0.1:${FRONTEND_PORT}`;
const BACKEND_BASE = 'http://127.0.0.1:8001';

test.describe('Resume Editor - Advanced Features', () => {
  let resumeId: string;

  test.beforeEach(async ({ page, request, context }) => {
    // Create test account and login
    const timestamp = Date.now();
    const email = `test${timestamp}@skillforge.com`;
    
    // Signup via backend
    await request.post(`${BACKEND_BASE}/api/v1/auth/signup`, {
      data: {
        email,
        password: 'Test1234!',
        full_name: 'Test User'
      }
    });

    // Login via Next.js proxy API to set HttpOnly cookie in browser context
    const loginResponse = await context.request.post(`${FRONTEND_BASE}/api/session/login`, {
      data: { email, password: 'Test1234!' }
    });
    
    expect(loginResponse.ok()).toBeTruthy();

    // Navigate to create resume (will auto-create on /resumes/new)
    await page.goto(`${FRONTEND_BASE}/resumes/new`, { waitUntil: 'domcontentloaded' });
    
    // Wait for either redirect to editor or editor to load
    await page.waitForURL(/\/resumes\/\d+/, { timeout: 15000 });
    
    const url = page.url();
    const match = url.match(/\/resumes\/(\d+)/);
    resumeId = match ? match[1] : '';
    
    expect(resumeId).toBeTruthy();
  });

  test('should display ATS score badge and open breakdown modal', async ({ page }) => {
    // Wait for ATS score to load
    await page.waitForSelector('button:has-text("ATS Score")', { timeout: 15000 });
    
    // Check if score is displayed
    const scoreElement = page.locator('button:has-text("ATS Score")');
    await expect(scoreElement).toBeVisible();
    
    // Click to open breakdown modal
    await scoreElement.click();
    
    // Check modal opened
    await expect(page.locator('text=ATS Analysis')).toBeVisible();
    await expect(page.locator('text=Overall ATS Score')).toBeVisible();
    await expect(page.locator('text=Formatting')).toBeVisible();
    await expect(page.locator('text=Keywords')).toBeVisible();
    await expect(page.locator('text=Content')).toBeVisible();
    
    // Close modal
    await page.locator('button[aria-label="Close"]').first().click();
    await expect(page.locator('text=ATS Analysis')).not.toBeVisible();
  });

  test('should toggle AI Assistant panel', async ({ page }) => {
    // Click AI Assistant button
    await page.locator('[data-testid="btn-ai-panel"]').click();
    
    // Check AI panel is visible
    await expect(page.locator('text=AI Assistant')).toBeVisible();
    await expect(page.locator('text=Summary')).toBeVisible();
    await expect(page.locator('text=Bullets')).toBeVisible();
    await expect(page.locator('text=Keywords')).toBeVisible();
    await expect(page.locator('text=Projects')).toBeVisible();
    
    // Live preview should be hidden
    await expect(page.locator('[data-testid="editor-live-preview"]')).not.toBeVisible();
    
    // Click again to close
    await page.locator('[data-testid="btn-ai-panel"]').click();
    
    // AI panel should be hidden, preview visible
    await page.waitForTimeout(500); // Animation time
    await expect(page.locator('[data-testid="editor-live-preview"]')).toBeVisible();
  });

  test('should generate AI summary suggestion', async ({ page }) => {
    // Open AI panel
    await page.locator('[data-testid="btn-ai-panel"]').click();
    
    // Click Summary tab (should be default)
    await page.locator('button:has-text("Summary")').click();
    
    // Click generate
    await page.locator('[data-testid="btn-ai-generate"]').click();
    
    // Wait for suggestions to appear
    await expect(page.locator('[data-testid="ai-suggestions"]')).toBeVisible({ timeout: 10000 });
    
    // Check suggestion content exists
    const suggestions = page.locator('[data-testid="ai-suggestions"] > div');
    await expect(suggestions.first()).toBeVisible();
  });

  test('should open template gallery and switch templates', async ({ page }) => {
    // Click Templates button
    await page.locator('button:has-text("Templates")').click();
    
    // Check modal opened
    await expect(page.locator('text=Choose Your Template')).toBeVisible();
    
    // Check all 4 templates are visible
    await expect(page.locator('text=Professional')).toBeVisible();
    await expect(page.locator('text=Modern')).toBeVisible();
    await expect(page.locator('text=Creative')).toBeVisible();
    await expect(page.locator('text=Minimal')).toBeVisible();
    
    // Click Modern template
    await page.locator('text=Modern').first().click();
    
    // Modal should close
    await expect(page.locator('text=Choose Your Template')).not.toBeVisible({ timeout: 3000 });
    
    // Check save status updated (resume was modified)
    await expect(page.locator('[data-testid="status-save"]')).toContainText(/Saved|Saving/);
  });

  test('should drag and reorder sections', async ({ page }) => {
    // Wait for sections to load
    await page.waitForSelector('text=Contact Info', { timeout: 5000 });
    
    // Get initial order
    const sections = page.locator('.space-y-3 > div');
    const firstSection = sections.first();
    const firstSectionText = await firstSection.textContent();
    
    // Perform drag operation (drag first section down)
    const firstBox = await firstSection.boundingBox();
    const secondBox = await sections.nth(1).boundingBox();
    
    if (firstBox && secondBox) {
      await page.mouse.move(firstBox.x + firstBox.width / 2, firstBox.y + firstBox.height / 2);
      await page.mouse.down();
      await page.mouse.move(secondBox.x + secondBox.width / 2, secondBox.y + secondBox.height / 2, { steps: 10 });
      await page.mouse.up();
      
      // Wait for animation
      await page.waitForTimeout(500);
      
      // Check order changed
      const newFirstSectionText = await sections.first().textContent();
      expect(newFirstSectionText).not.toBe(firstSectionText);
    }
  });

  test('should toggle section visibility', async ({ page }) => {
    // Wait for sections to load
    await page.waitForSelector('text=Certificates', { timeout: 5000 });
    
    // Find Certificates section checkbox
    const certificatesSection = page.locator('button:has-text("Certificates")').locator('..');
    const checkbox = certificatesSection.locator('input[type="checkbox"]');
    
    // Check initial state
    const isChecked = await checkbox.isChecked();
    
    // Toggle checkbox
    await checkbox.click();
    
    // Wait for state change
    await page.waitForTimeout(300);
    
    // Verify state changed
    const newIsChecked = await checkbox.isChecked();
    expect(newIsChecked).toBe(!isChecked);
  });

  test('should auto-save resume changes', async ({ page }) => {
    // Edit resume title
    const titleInput = page.locator('[data-testid="input-title"]');
    await titleInput.fill('My Updated Resume Title');
    
    // Wait for auto-save (2 second debounce)
    await page.waitForTimeout(2500);
    
    // Check save status shows "Saved"
    await expect(page.locator('[data-testid="status-save"]')).toContainText(/Saved \d+:\d+/);
    
    // Reload page
    await page.reload();
    
    // Wait for editor to load
    await page.waitForSelector('[data-testid="input-title"]');
    
    // Check title persisted
    await expect(titleInput).toHaveValue('My Updated Resume Title');
  });

  test('should export PDF', async ({ page }) => {
    // Click export button
    const exportButton = page.locator('[data-testid="btn-export-pdf"]');
    
    // Start download
    const downloadPromise = page.waitForEvent('download', { timeout: 15000 });
    await exportButton.click();
    
    // Wait for download
    const download = await downloadPromise;
    
    // Check filename
    const filename = download.suggestedFilename();
    expect(filename).toMatch(/\.pdf$/);
  });

  test('should open full preview in new tab', async ({ page, context }) => {
    // Click preview button
    const previewButton = page.locator('[data-testid="btn-full-preview"]');
    
    // Wait for new page
    const pagePromise = context.waitForEvent('page');
    await previewButton.click();
    
    const newPage = await pagePromise;
    await newPage.waitForLoadState();
    
    // Check URL
    expect(newPage.url()).toContain(`/resumes/${resumeId}/preview`);
    
    // Close new tab
    await newPage.close();
  });

  test('should switch between editor sections', async ({ page }) => {
    // Wait for sections to load
    await page.waitForSelector('text=Contact Info', { timeout: 5000 });
    
    // Click Experience section
    await page.locator('button:has-text("Work Experience")').click();
    
    // Check active state (should have forgePurple background)
    const experienceSection = page.locator('button:has-text("Work Experience")').locator('..');
    await expect(experienceSection).toHaveClass(/forgePurple/);
    
    // Click Skills section
    await page.locator('button:has-text("Skills")').click();
    
    // Check active state changed
    const skillsSection = page.locator('button:has-text("Skills")').locator('..');
    await expect(skillsSection).toHaveClass(/forgePurple/);
    await expect(experienceSection).not.toHaveClass(/forgePurple/);
  });

  test('should handle AI generation errors gracefully', async ({ page }) => {
    // Open AI panel
    await page.locator('[data-testid="btn-ai-panel"]').click();
    
    // Switch to Bullets tab (requires work experience)
    await page.locator('button:has-text("Bullets")').click();
    
    // Try to generate without work experience
    await page.locator('[data-testid="btn-ai-generate"]').click();
    
    // Should show error message
    await expect(page.locator('text=Add work experience first')).toBeVisible({ timeout: 5000 });
  });
});
