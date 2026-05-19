import { test, expect } from '@playwright/test'

test('contact page renders form fields', async ({ page }) => {
  await page.goto('/contacto')
  await expect(page.getByPlaceholder('Nombre')).toBeVisible()
  await expect(page.getByPlaceholder('Email')).toBeVisible()
  await expect(page.getByRole('button', { name: /Quiero información/i })).toBeVisible()
})

test('empty form submission stays on page', async ({ page }) => {
  await page.goto('/contacto')
  await page.getByRole('button', { name: /Quiero información/i }).click()
  await expect(page).toHaveURL('/contacto')
})
