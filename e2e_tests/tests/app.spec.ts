/**
 * E2E Tests for Budget App
 * Following webapp-testing skill patterns with Playwright
 */

import { test, expect } from '@playwright/test';

// Test data
const testUser = {
  name: 'Test User',
  email: `test${Date.now()}@example.com`,
  password: 'TestPass123'
};

test.describe('Budget App E2E Tests', () => {
  
  test('should display login page on load', async ({ page }) => {
    // Use baseURL from config (supports Docker and local)
    await page.goto('/');
    
    // Verify login page elements
    await expect(page.locator('#login-page .brand-title')).toContainText('BudgetFlow');
    await expect(page.locator('#login-email')).toBeVisible();
    await expect(page.locator('#login-password')).toBeVisible();
    await expect(page.locator('#login-page button[type="submit"]')).toBeVisible();
  });
  
  test('should navigate to registration page', async ({ page }) => {
    await page.goto('/');
    
    // Click "Create one" link
    await page.click('#show-register');
    
    // Verify registration form is visible
    await expect(page.locator('#register-page')).toBeVisible();
    await expect(page.locator('#register-name')).toBeVisible();
    await expect(page.locator('#register-email')).toBeVisible();
    await expect(page.locator('#register-password')).toBeVisible();
  });
  
  test('should validate password requirements on registration', async ({ page }) => {
    await page.goto('/');
    await page.click('#show-register');
    
    // Fill form with weak password
    await page.fill('#register-name', testUser.name);
    await page.fill('#register-email', testUser.email);
    await page.fill('#register-password', 'weak');
    
    // Submit form - scope to register page
    await page.locator('#register-page button[type="submit"]').click();
    
    // Verify error message appears (Pydantic validation message)
    await expect(page.locator('#register-error')).toBeVisible();
    await expect(page.locator('#register-error')).toContainText(/at least 8 characters|password/i);
  });
  
  test('should register new user and auto-login', async ({ page }) => {
    await page.goto('/');
    await page.click('#show-register');
    
    // Fill registration form
    await page.fill('#register-name', testUser.name);
    await page.fill('#register-email', testUser.email);
    await page.fill('#register-password', testUser.password);
    
    // Submit form - scope to register page
    await page.locator('#register-page button[type="submit"]').click();
    
    // Wait for dashboard to load
    await page.waitForSelector('#dashboard-container', { state: 'visible', timeout: 10000 });
    
    // Verify dashboard elements
    await expect(page.locator('.nav-brand')).toContainText('BudgetFlow');
    await expect(page.locator('#current-balance')).toBeVisible();
    await expect(page.locator('#total-income')).toBeVisible();
    await expect(page.locator('#total-expenses')).toBeVisible();
  });
  
  test('should add income transaction', async ({ page }) => {
    // Register and login
    await page.goto('/');
    await page.click('#show-register');
    await page.fill('#register-name', testUser.name);
    await page.fill('#register-email', `income${Date.now()}@example.com`);
    await page.fill('#register-password', testUser.password);
    await page.locator('#register-page button[type="submit"]').click();
    
    await page.waitForSelector('#dashboard-container', { state: 'visible', timeout: 10000 });
    
    // Verify initial balance is $0.00
    await expect(page.locator('#current-balance')).toContainText('$0.00');
    
    // Add income transaction
    await page.selectOption('#transaction-type', 'income');
    await page.selectOption('#transaction-category', 'salary');
    await page.fill('#transaction-amount', '5000');
    await page.fill('#transaction-description', 'Monthly salary');
    
    await page.click('#transaction-form button[type="submit"]');
    
    // Wait for transaction to be added
    await page.waitForTimeout(1000);
    
    // Verify balance updated
    await expect(page.locator('#current-balance')).toContainText('$5,000.00');
    await expect(page.locator('#total-income')).toContainText('$5,000.00');
    
    // Verify transaction appears in list
    await expect(page.locator('.transactions-list')).toContainText('Salary');
    await expect(page.locator('.transactions-list')).toContainText('Monthly salary');
    await expect(page.locator('.transactions-list')).toContainText('+$5,000.00');
  });
  
  test('should add expense transaction', async ({ page }) => {
    // Register and login
    await page.goto('/');
    await page.click('#show-register');
    await page.fill('#register-name', testUser.name);
    await page.fill('#register-email', `expense${Date.now()}@example.com`);
    await page.fill('#register-password', testUser.password);
    await page.locator('#register-page button[type="submit"]').click();
    
    await page.waitForSelector('#dashboard-container', { state: 'visible', timeout: 10000 });
    
    // Add expense transaction
    await page.selectOption('#transaction-type', 'expense');
    await page.selectOption('#transaction-category', 'food');
    await page.fill('#transaction-amount', '150.50');
    await page.fill('#transaction-description', 'Grocery shopping');
    
    await page.click('#transaction-form button[type="submit"]');
    
    // Wait for transaction to be added
    await page.waitForTimeout(1000);
    
    // Verify balance updated (negative)
    await expect(page.locator('#current-balance')).toContainText('-$150.50');
    await expect(page.locator('#total-expenses')).toContainText('$150.50');
    
    // Verify transaction appears in list
    await expect(page.locator('.transactions-list')).toContainText('Food');
    await expect(page.locator('.transactions-list')).toContainText('-$150.50');
  });
  
  test('should calculate correct balance with multiple transactions', async ({ page }) => {
    // Register and login
    await page.goto('/');
    await page.click('#show-register');
    await page.fill('#register-name', testUser.name);
    await page.fill('#register-email', `balance${Date.now()}@example.com`);
    await page.fill('#register-password', testUser.password);
    await page.locator('#register-page button[type="submit"]').click();
    
    await page.waitForSelector('#dashboard-container', { state: 'visible', timeout: 10000 });
    
    // Add income: $3000
    await page.selectOption('#transaction-type', 'income');
    await page.selectOption('#transaction-category', 'salary');
    await page.fill('#transaction-amount', '3000');
    await page.click('#transaction-form button[type="submit"]');
    await page.waitForTimeout(500);
    
    // Add expense: $500
    await page.selectOption('#transaction-type', 'expense');
    await page.selectOption('#transaction-category', 'housing');
    await page.fill('#transaction-amount', '500');
    await page.click('#transaction-form button[type="submit"]');
    await page.waitForTimeout(500);
    
    // Add expense: $200
    await page.selectOption('#transaction-type', 'expense');
    await page.selectOption('#transaction-category', 'food');
    await page.fill('#transaction-amount', '200');
    await page.click('#transaction-form button[type="submit"]');
    await page.waitForTimeout(1000);
    
    // Verify balance: 3000 - 500 - 200 = 2300
    await expect(page.locator('#current-balance')).toContainText('$2,300.00');
    await expect(page.locator('#total-income')).toContainText('$3,000.00');
    await expect(page.locator('#total-expenses')).toContainText('$700.00');
  });
  
  test('should delete transaction', async ({ page }) => {
    // Register and login
    await page.goto('/');
    await page.click('#show-register');
    await page.fill('#register-name', testUser.name);
    await page.fill('#register-email', `delete${Date.now()}@example.com`);
    await page.fill('#register-password', testUser.password);
    await page.locator('#register-page button[type="submit"]').click();
    
    await page.waitForSelector('#dashboard-container', { state: 'visible', timeout: 10000 });
    
    // Add a transaction
    await page.selectOption('#transaction-type', 'income');
    await page.selectOption('#transaction-category', 'salary');
    await page.fill('#transaction-amount', '1000');
    await page.click('#transaction-form button[type="submit"]');
    await page.waitForTimeout(1000);
    
    // Verify transaction exists
    await expect(page.locator('.transactions-list')).toContainText('$1,000.00');
    
    // Setup dialog handler for confirmation
    page.on('dialog', dialog => dialog.accept());
    
    // Click delete button
    await page.click('.transaction-delete');
    await page.waitForTimeout(1000);
    
    // Verify balance is back to $0.00
    await expect(page.locator('#current-balance')).toContainText('$0.00');
    await expect(page.locator('.transactions-list')).toContainText('No transactions yet');
  });
  
  test('should logout user', async ({ page }) => {
    // Register and login
    await page.goto('/');
    await page.click('#show-register');
    await page.fill('#register-name', testUser.name);
    await page.fill('#register-email', `logout${Date.now()}@example.com`);
    await page.fill('#register-password', testUser.password);
    await page.locator('#register-page button[type="submit"]').click();
    
    await page.waitForSelector('#dashboard-container', { state: 'visible', timeout: 10000 });
    
    // Click logout
    await page.click('#logout-btn');
    
    // Verify redirected to login page
    await expect(page.locator('#auth-container')).toBeVisible();
    await expect(page.locator('#login-page')).toBeVisible();
  });
  
  test('should show error for invalid login', async ({ page }) => {
    await page.goto('/');
    
    // Try to login with invalid credentials
    await page.fill('#login-email', 'nonexistent@example.com');
    await page.fill('#login-password', 'WrongPassword123');
    await page.locator('#login-page button[type="submit"]').click();
    
    // Verify error message
    await expect(page.locator('#login-error')).toBeVisible();
    await expect(page.locator('#login-error')).toContainText(/incorrect/i);
  });
  
  test('should validate required fields', async ({ page }) => {
    await page.goto('/');
    await page.click('#show-register');
    
    // Submit empty form - scope to register page
    await page.locator('#register-page button[type="submit"]').click();
    
    // Verify form validation (browser native validation)
    const nameInput = page.locator('#register-name');
    await expect(nameInput).toHaveAttribute('required');
  });
});
