import { test, expect } from '@playwright/test';

test('board columns render', async ({ page }) => {
  await page.goto('/board');
  for (const name of ['TODO','IN_PROGRESS','REVIEW','DONE']) {
    await expect(page.getByText(name)).toBeVisible();
  }
});

test('backlog table headers render', async ({ page }) => {
  await page.goto('/backlog');
  for (const h of ['ID','Título','Prior.','Status','Assignee','Order','Ações']) {
    await expect(page.getByText(h)).toBeVisible();
  }
});

test('yaml studio loads and validates', async ({ page }) => {
  await page.goto('/yaml-studio');
  await page.getByText('Carregar').click();
  await page.getByText('Validar').click();
  await expect(page.getByText('Erros')).toBeVisible();
});
