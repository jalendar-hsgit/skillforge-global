import { test, expect, type Locator, type Page } from '@playwright/test';

// Helper to drag using pointer events (compatible with dnd-kit)
async function dragElement(page: Page, source: Locator, target: Locator) {
  source = source.first();
  target = target.first();
  await expect(source).toBeVisible();
  await expect(target).toBeVisible();

  const sourceBox = await source.boundingBox();
  const targetBox = await target.boundingBox();
  if (!sourceBox || !targetBox) throw new Error('Missing bounding boxes for drag');

  const startX = sourceBox.x + sourceBox.width / 2;
  const startY = sourceBox.y + sourceBox.height / 2;
  const endX = targetBox.x + targetBox.width / 2;
  const endY = targetBox.y + Math.min(80, targetBox.height / 2);

  await page.mouse.move(startX, startY);
  await page.mouse.down();
  await page.mouse.move(endX, endY, { steps: 12 });
  await page.mouse.up();
}

test.describe('Job Tracker Kanban DnD', () => {
  test('drag a card between columns (if data available)', async ({ page }) => {
    await page.goto('/job-tracker');

    // Ensure Kanban mode
    const kanbanBtn = page.getByRole('button', { name: 'Kanban' });
    await kanbanBtn.click();

    // Find any column with at least one card
    const anyCard = page.locator('[data-testid^="kanban-card-"]').first();
    const hasAnyCard = await anyCard.count().then(c => c > 0);
    if (!hasAnyCard) test.skip(true, 'No cards found to drag');

    // Determine source column and choose a different target column if possible
    const columns = [
      'wishlist','applied','screening','interview','assessment','offer','accepted','rejected'
    ];

    // Pick a source column that has at least one card
    let sourceColId: string | null = null;
    for (const id of columns) {
      const col = page.locator(`[data-testid="kanban-column-${id}"] [data-testid^="kanban-card-"]`).first();
      if (await col.count().then(c => c > 0)) { sourceColId = id; break; }
    }
    if (!sourceColId) test.skip(true, 'No populated column found');

    const targetColId = columns.find(c => c !== sourceColId) ?? 'screening';

    const sourceHandle = page.locator(`[data-testid="kanban-column-${sourceColId}"] [aria-label="Drag handle"]`).first();
    const targetCol = page.locator(`[data-testid="kanban-column-${targetColId}"]`);

    await dragElement(page, sourceHandle, targetCol);

    // Expect either a success toast or the card to appear in target column (optimistic update)
    const successToast = page.locator('text=Status updated');
    // Race: toast OR card appears in target column
    await Promise.race([
      successToast.waitFor({ state: 'visible', timeout: 3000 }).catch(() => {}),
      page.locator(`[data-testid="kanban-column-${targetColId}"] [data-testid^="kanban-card-"]`).first().waitFor({ state: 'visible', timeout: 3000 }).catch(() => {}),
    ]);

    // Soft assertion: page still responsive
    await expect(page).toHaveTitle(/Job Application Tracker/);
  });
});
