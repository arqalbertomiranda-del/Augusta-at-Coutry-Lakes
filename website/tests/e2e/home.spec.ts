import { test, expect } from '@playwright/test'

test('home page loads with hero heading', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toBeVisible()
  await expect(page.locator('h1')).toContainText('campo de golf')
})

test('stats bar is visible', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('18 hoyos')).toBeVisible()
  await expect(page.getByText('Campo Greg Letsche')).toBeVisible()
})

test('nav links are visible', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('link', { name: 'Ver disponibilidad' }).first()).toBeVisible()
})
