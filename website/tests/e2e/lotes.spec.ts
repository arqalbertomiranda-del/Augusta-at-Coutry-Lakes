import { test, expect } from '@playwright/test'

test('lotes page renders heading', async ({ page }) => {
  await page.goto('/lotes')
  await expect(page.locator('h1')).toContainText('Lotes disponibles')
})

test('filter buttons are visible', async ({ page }) => {
  await page.goto('/lotes')
  await expect(page.getByRole('button', { name: 'Todos' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Disponibles' })).toBeVisible()
})
