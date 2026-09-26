# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests/brain_features.spec.ts >> BrainVault Displays New Futuristic Features
- Location: tests/brain_features.spec.ts:3:1

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5174/brain-vault
Call log:
  - navigating to "http://localhost:5174/brain-vault", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  |
  3  | test('BrainVault Displays New Futuristic Features', async ({ page }) => {
  4  |   // Mock API for BrainVault content
  5  |   await page.route('**/api/automation/content*', async (route) => {
  6  |     await route.fulfill({
  7  |       status: 200,
  8  |       contentType: 'application/json',
  9  |       body: JSON.stringify({
  10 |         success: true,
  11 |         data: [
  12 |           {
  13 |             id: 1,
  14 |             content_type: 'subject_book',
  15 |             topic: 'Economy of India',
  16 |             created_at: new Date().toISOString(),
  17 |             content: JSON.stringify({
  18 |               title: "Economy of India",
  19 |               chapters: [{ title: "Banking", content: "# Banking System\nRBI is...", key_concepts: ["RBI"] }]
  20 |             })
  21 |           },
  22 |           {
  23 |             id: 2,
  24 |             content_type: 'heatmap',
  25 |             topic: 'Study Weaknesses',
  26 |             created_at: new Date().toISOString(),
  27 |             content: JSON.stringify([
  28 |               { name: "History", size: 100, intensity: 80 },
  29 |               { name: "Polity", size: 50, intensity: 20 }
  30 |             ])
  31 |           },
  32 |           {
  33 |             id: 3,
  34 |             content_type: 'interview_sim',
  35 |             topic: 'Civil Service Interview',
  36 |             created_at: new Date().toISOString(),
  37 |             content: JSON.stringify([{ sender: 'board', text: 'Welcome', timestamp: new Date() }])
  38 |           },
  39 |           {
  40 |             id: 4,
  41 |             content_type: 'self_review',
  42 |             topic: 'Weekly Review',
  43 |             created_at: new Date().toISOString(),
  44 |             content: JSON.stringify({
  45 |               week: '2025-W10',
  46 |               stats: { total: 10, success_rate: 90, avg_impact: 0.8 },
  47 |               improvement_plan: { plan: ["Study more"] }
  48 |             })
  49 |           }
  50 |         ]
  51 |       })
  52 |     });
  53 |   });
  54 |
  55 |   // Navigate to Brain Vault (assuming route, but we might need to click nav)
> 56 |   await page.goto('http://localhost:5174/brain-vault'); // Adjusted route
     |              ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5174/brain-vault
  57 |
  58 |   // Check if items list loaded
  59 |   await expect(page.getByText('Economy of India')).toBeVisible();
  60 |
  61 |   // Test Subject Book
  62 |   await page.getByText('Economy of India').click();
  63 |   await expect(page.locator('.subject-book-container')).toBeVisible();
  64 |   await expect(page.getByText('Chapter 1: Banking')).toBeVisible();
  65 |
  66 |   // Test Heatmap
  67 |   await page.getByText('Study Weaknesses').click();
  68 |   await expect(page.locator('.heatmap-container')).toBeVisible();
  69 |
  70 |   // Test Interview Sim
  71 |   await page.getByText('Civil Service Interview').click();
  72 |   await expect(page.locator('.interview-sim-container')).toBeVisible();
  73 |   await expect(page.getByText('UPSC Interview Board Simulator')).toBeVisible();
  74 |
  75 |   // Test Self Review
  76 |   await page.getByText('Weekly Review').click();
  77 |   await expect(page.locator('.self-review-container')).toBeVisible();
  78 |   await expect(page.getByText('Weekly System Review')).toBeVisible();
  79 | });
  80 |
```