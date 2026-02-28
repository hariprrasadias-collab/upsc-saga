import { test, expect } from '@playwright/test';

test('Verify ChallengeCard accessibility and presence', async ({ page }) => {
  // Navigate to the dashboard
  await page.goto('http://localhost:5173/');

  // Wait for the ChallengeCard to load
  const challengeCard = page.locator('.challenge-card');
  await expect(challengeCard).toBeVisible();

  // Verify accessibility attributes on the progress bar
  const progressBar = page.locator('.challenge-progress');
  await expect(progressBar).toHaveAttribute('role', 'progressbar');
  await expect(progressBar).toHaveAttribute('aria-label', /Daily Challenge Progress/);

  // Take a screenshot of the ChallengeCard
  await challengeCard.screenshot({ path: 'challenge_card_verification.png' });
});
