import { test, expect } from '@playwright/test'

const email = `e2e-${Date.now()}@example.test`
const password = 'LocalE2E123!'

test('client critical fraud case flow', async ({ page }) => {
  await page.goto('/register')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password').fill(password)
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page.getByRole('heading', { name: 'Your SafeNestT dashboard' })).toBeVisible()

  await page.getByRole('link', { name: 'Report a Scam' }).first().click()
  await page.getByLabel('Case type').selectOption({ label: 'Online scam' })
  await page.getByLabel('What happened?').fill('A scammer contacted me and requested a suspicious payment. This is an E2E case.')
  await page.getByRole('button', { name: 'Create Case' }).click()
  await expect(page.getByRole('heading', { name: /Online scam report/ })).toBeVisible()

  await page.getByLabel('Evidence label').fill('Suspicious message')
  await page.getByLabel('Evidence / notes').fill('Preserved scam message for investigation.')
  await page.getByRole('button', { name: 'Add Evidence' }).click()
  await expect(page.getByText('Suspicious message')).toBeVisible()

  await page.getByRole('button', { name: 'Start AI Investigation' }).click()
  await expect(page.getByText(/Case intake completed|SafeNestT AI investigation completed|AI service unavailable/)).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Findings' })).toBeVisible()
})
