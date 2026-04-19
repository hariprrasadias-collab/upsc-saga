import { test, expect } from '@playwright/test';

test('BrainVault Displays New Futuristic Features', async ({ page }) => {
  // Mock API for BrainVault content
  await page.route('**/api/automation/content*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: [
          {
            id: 1,
            content_type: 'subject_book',
            topic: 'Economy of India',
            created_at: new Date().toISOString(),
            content: JSON.stringify({
              title: "Economy of India",
              chapters: [{ title: "Banking", content: "# Banking System\nRBI is...", key_concepts: ["RBI"] }]
            })
          },
          {
            id: 2,
            content_type: 'heatmap',
            topic: 'Study Weaknesses',
            created_at: new Date().toISOString(),
            content: JSON.stringify([
              { name: "History", size: 100, intensity: 80 },
              { name: "Polity", size: 50, intensity: 20 }
            ])
          },
          {
            id: 3,
            content_type: 'interview_sim',
            topic: 'Civil Service Interview',
            created_at: new Date().toISOString(),
            content: JSON.stringify([{ sender: 'board', text: 'Welcome', timestamp: new Date() }])
          },
          {
            id: 4,
            content_type: 'self_review',
            topic: 'Weekly Review',
            created_at: new Date().toISOString(),
            content: JSON.stringify({
              week: '2025-W10',
              stats: { total: 10, success_rate: 90, avg_impact: 0.8 },
              improvement_plan: { plan: ["Study more"] }
            })
          }
        ]
      })
    });
  });

  // Navigate to Brain Vault (assuming route, but we might need to click nav)
  await page.goto('http://localhost:5174/brain-vault'); // Adjusted route

  // Check if items list loaded
  await expect(page.getByText('Economy of India')).toBeVisible();

  // Test Subject Book
  await page.getByText('Economy of India').click();
  await expect(page.locator('.subject-book-container')).toBeVisible();
  await expect(page.getByText('Chapter 1: Banking')).toBeVisible();

  // Test Heatmap
  await page.getByText('Study Weaknesses').click();
  await expect(page.locator('.heatmap-container')).toBeVisible();

  // Test Interview Sim
  await page.getByText('Civil Service Interview').click();
  await expect(page.locator('.interview-sim-container')).toBeVisible();
  await expect(page.getByText('UPSC Interview Board Simulator')).toBeVisible();

  // Test Self Review
  await page.getByText('Weekly Review').click();
  await expect(page.locator('.self-review-container')).toBeVisible();
  await expect(page.getByText('Weekly System Review')).toBeVisible();
});
