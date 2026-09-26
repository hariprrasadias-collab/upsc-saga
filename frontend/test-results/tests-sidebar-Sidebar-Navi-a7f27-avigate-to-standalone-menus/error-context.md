# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests/sidebar.spec.ts >> Sidebar Navigation E2E Tests >> should navigate to standalone menus
- Location: tests/sidebar.spec.ts:5:5

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5174/
Call log:
  - navigating to "http://localhost:5174/", waiting until "load"

```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   |
  3   | test.describe('Sidebar Navigation E2E Tests', () => {
  4   |     // Test standalone menus
  5   |     test('should navigate to standalone menus', async ({ page }) => {
> 6   |         await page.goto('http://localhost:5174');
      |                    ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5174/
  7   |
  8   |         // Wait for sidebar to be ready
  9   |         const sidebar = page.locator('.sidebar');
  10  |         await expect(sidebar).toBeVisible();
  11  |
  12  |         // Analytics
  13  |         await page.click('button:has-text("Analytics")');
  14  |         // Wait for Analytics component to render
  15  |         await expect(page.locator('.analytics-container, text="Analytics Dashboard", text="Study Stats"').first()).toBeVisible({ timeout: 5000 });
  16  |
  17  |         // Weak Areas
  18  |         await page.click('button:has-text("Weak Areas")');
  19  |         await expect(page.locator('.weak-areas-container, text="Weak Areas", text="Critical Gaps"').first()).toBeVisible({ timeout: 5000 });
  20  |     });
  21  |
  22  |     // Test expanding groups and nested items
  23  |     const menuGroups = [
  24  |         {
  25  |             groupName: '🗺️ Planning',
  26  |             items: [
  27  |                 { name: 'Study Plan', url: '/study-plan' },
  28  |                 { name: 'War Map', url: '/war-map' },
  29  |                 { name: 'War Room Archives', url: '/triangulation-history' },
  30  |                 { name: 'Syllabus', url: '/syllabus' },
  31  |                 { name: 'Quests', url: '/quests' },
  32  |                 { name: 'Revision Cards', url: '/revision-cards' },
  33  |                 { name: 'Mnemonics', url: '/mnemonics' },
  34  |                 { name: 'Mind Map', url: '/mindmap' },
  35  |                 { name: 'Mind Palace', url: '/mind-palace' },
  36  |                 { name: 'Revision Center', url: '/revision-center' },
  37  |                 { name: 'Time Boxing', url: '/timebox' },
  38  |                 { name: 'The Golden Path', url: '/golden-path' }
  39  |             ]
  40  |         },
  41  |         {
  42  |             groupName: '💪 Training',
  43  |             items: [
  44  |                 { name: 'Anki Dojo', url: '/dojo' },
  45  |                 { name: 'Answer Writing', url: '/answer-writing' },
  46  |                 { name: 'The Scribe (AI)', url: '/scribe' },
  47  |                 { name: 'Socratic Archives', url: '/socratic-history' },
  48  |                 { name: 'Mock Tests', url: '/mock-tests' },
  49  |                 { name: 'Boss Arena', url: '/arena' },
  50  |                 { name: 'Essay Workshop', url: '/essay' },
  51  |                 { name: 'CSAT Prep', url: '/csat' },
  52  |                 { name: 'Project Foresight', url: '/foresight' }
  53  |             ]
  54  |         },
  55  |         {
  56  |             groupName: '📚 Knowledge',
  57  |             items: [
  58  |                 { name: 'Mimir (AI)', isModal: true },
  59  |                 { name: 'Brain Vault', url: '/brain-vault' },
  60  |                 { name: 'Flashcards', url: '/flashcards' },
  61  |                 { name: 'The Seer', url: '/seer' },
  62  |                 { name: 'The Ravens', url: '/ravens' },
  63  |                 { name: 'Monthly Compilation', url: '/compilation' },
  64  |                 { name: 'The Archives', url: '/pyq' },
  65  |                 { name: 'PYQ Heatmap', url: '/heatmap' },
  66  |                 { name: 'Model Answers', url: '/model-answers' },
  67  |                 { name: 'Yggdrasil', url: '/codex' },
  68  |                 { name: 'Lore Tablets', url: '/lore-tablets' },
  69  |                 { name: 'Night Watchman', url: '/watchman' }
  70  |             ]
  71  |         },
  72  |         {
  73  |             groupName: '⚡ Enhancement',
  74  |             items: [
  75  |                 { name: 'Armory', url: '/armory' },
  76  |                 { name: 'The Panopticon', url: '/panopticon' },
  77  |                 { name: 'The Neural Hash', url: '/neural-hash' }
  78  |             ]
  79  |         },
  80  |         {
  81  |             groupName: '🛡️ Admin',
  82  |             items: [
  83  |                 { name: 'Control Panel', url: '/admin' }
  84  |             ]
  85  |         }
  86  |     ];
  87  |
  88  |     for (const group of menuGroups) {
  89  |         test(`should navigate to every item in ${group.groupName}`, async ({ page }) => {
  90  |             await page.goto('http://localhost:5174');
  91  |
  92  |             // Expand the group if not already expanded (planning is expanded by default)
  93  |             if (group.groupName !== '🗺️ Planning') {
  94  |                 const groupButton = page.locator(`button.group-header:has-text("${group.groupName}")`);
  95  |                 const isExpanded = await groupButton.getAttribute('aria-expanded');
  96  |                 if (isExpanded === 'false') {
  97  |                     await groupButton.click();
  98  |                 }
  99  |             }
  100 |
  101 |             // Check each item
  102 |             for (const item of group.items) {
  103 |                 const itemButton = page.locator(`.group-items button:has-text("${item.name}")`);
  104 |                 await expect(itemButton).toBeVisible();
  105 |                 await itemButton.click();
  106 |
```