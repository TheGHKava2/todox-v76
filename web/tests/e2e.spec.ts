import { test, expect } from '@playwright/test';

test('dashboard loads and has navigation', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('ToDoX v5')).toBeVisible();
  await expect(page.getByText('Dashboard')).toBeVisible();
  await expect(page.getByText('Backlog')).toBeVisible();
  await expect(page.getByText('YAML Studio')).toBeVisible();
});
