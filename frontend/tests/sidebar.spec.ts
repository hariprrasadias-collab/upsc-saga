import { test, expect } from '@playwright/test';

test.describe('Sidebar Navigation E2E Tests', () => {
    // Test standalone menus
    test('should navigate to standalone menus', async ({ page }) => {
        await page.goto('http://localhost:5173');

        // Wait for sidebar to be ready
        const sidebar = page.locator('.sidebar');
        await expect(sidebar).toBeVisible();

        // Analytics
        await page.click('button:has-text("Analytics")');
        // Wait for Analytics component to render
        await expect(page.locator('.analytics-container, text="Analytics Dashboard", text="Study Stats"').first()).toBeVisible({ timeout: 5000 });

        // Weak Areas
        await page.click('button:has-text("Weak Areas")');
        await expect(page.locator('.weak-areas-container, text="Weak Areas", text="Critical Gaps"').first()).toBeVisible({ timeout: 5000 });
    });

    // Test expanding groups and nested items
    const menuGroups = [
        {
            groupName: '🗺️ Planning',
            items: [
                { name: 'Study Plan', url: '/study-plan' },
                { name: 'War Map', url: '/war-map' },
                { name: 'War Room Archives', url: '/triangulation-history' },
                { name: 'Syllabus', url: '/syllabus' },
                { name: 'Quests', url: '/quests' },
                { name: 'Revision Cards', url: '/revision-cards' },
                { name: 'Mnemonics', url: '/mnemonics' },
                { name: 'Mind Map', url: '/mindmap' },
                { name: 'Mind Palace', url: '/mind-palace' },
                { name: 'Revision Center', url: '/revision-center' },
                { name: 'Time Boxing', url: '/timebox' },
                { name: 'The Golden Path', url: '/golden-path' }
            ]
        },
        {
            groupName: '💪 Training',
            items: [
                { name: 'Anki Dojo', url: '/dojo' },
                { name: 'Answer Writing', url: '/answer-writing' },
                { name: 'The Scribe (AI)', url: '/scribe' },
                { name: 'Socratic Archives', url: '/socratic-history' },
                { name: 'Mock Tests', url: '/mock-tests' },
                { name: 'Boss Arena', url: '/arena' },
                { name: 'Essay Workshop', url: '/essay' },
                { name: 'CSAT Prep', url: '/csat' },
                { name: 'Project Foresight', url: '/foresight' }
            ]
        },
        {
            groupName: '📚 Knowledge',
            items: [
                { name: 'Mimir (AI)', isModal: true },
                { name: 'Brain Vault', url: '/brain-vault' },
                { name: 'Flashcards', url: '/flashcards' },
                { name: 'The Seer', url: '/seer' },
                { name: 'The Ravens', url: '/ravens' },
                { name: 'Monthly Compilation', url: '/compilation' },
                { name: 'The Archives', url: '/pyq' },
                { name: 'PYQ Heatmap', url: '/heatmap' },
                { name: 'Model Answers', url: '/model-answers' },
                { name: 'Yggdrasil', url: '/codex' },
                { name: 'Lore Tablets', url: '/lore-tablets' },
                { name: 'Night Watchman', url: '/watchman' }
            ]
        },
        {
            groupName: '⚡ Enhancement',
            items: [
                { name: 'Armory', url: '/armory' },
                { name: 'The Panopticon', url: '/panopticon' },
                { name: 'The Neural Hash', url: '/neural-hash' }
            ]
        },
        {
            groupName: '🛡️ Admin',
            items: [
                { name: 'Control Panel', url: '/admin' }
            ]
        }
    ];

    for (const group of menuGroups) {
        test(`should navigate to every item in ${group.groupName}`, async ({ page }) => {
            await page.goto('http://localhost:5173');

            // Expand the group if not already expanded (planning is expanded by default)
            if (group.groupName !== '🗺️ Planning') {
                const groupButton = page.locator(`button.group-header:has-text("${group.groupName}")`);
                const isExpanded = await groupButton.getAttribute('aria-expanded');
                if (isExpanded === 'false') {
                    await groupButton.click();
                }
            }

            // Check each item
            for (const item of group.items) {
                const itemButton = page.locator(`.group-items button:has-text("${item.name}")`);
                await expect(itemButton).toBeVisible();
                await itemButton.click();

                if (item.isModal) {
                    // Verify modal opens
                    const mimirModal = page.locator('.mimir-modal-backdrop, .mimir-chat-window');
                    await expect(mimirModal.first()).toBeVisible({ timeout: 5000 });
                    await page.click('.close-btn, .mimir-modal-backdrop'); // Close it back to prevent blocking
                } else {
                    // Make sure Vite syntax error overlay is NOT visible
                    await expect(page.locator('vite-error-overlay')).toHaveCount(0);
                }
            }
        });
    }
});
