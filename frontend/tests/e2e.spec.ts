/**
 * QuantumShield Vault - Frontend Tests with Playwright
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('QuantumShield Vault - E2E Tests', () => {
  test('Homepage loads successfully', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/QuantumShield Vault/);
  });

  test('API documentation accessible', async ({ page }) => {
    await page.goto(`${BASE_URL.replace('3000', '8000')}/docs`);
    await expect(page.locator('text=FastAPI')).toBeVisible();
  });

  test('Health check endpoint responds', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL.replace('3000', '8000')}/health`);
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });
});
