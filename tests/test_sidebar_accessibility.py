import sys

from playwright.sync_api import Page, expect, sync_playwright

def test_sidebar_accessibility(page: Page):
    # Route the dashboard API request to just return a dummy successful response
    # to avoid "ERROR: FAILED TO FETCH DASHBOARD DATA" which blocks the UI
    page.route("**/api/dashboard*", lambda route: route.fulfill(status=200, json={}))
    page.route("**/api/auth*", lambda route: route.fulfill(status=200, json={"user": "test"}))
    page.route("**/api/**", lambda route: route.fulfill(status=200, json={}))

    page.goto("http://localhost:5173")

    # Wait for the sidebar to be visible
    sidebar = page.locator('.sidebar')
    sidebar.wait_for(state='visible')

    # Check the aria-controls and id attributes on the expandable groups
    planning_button = page.locator('button.group-header:has-text("🗺️ Planning")')
    expect(planning_button).to_have_attribute('aria-controls', 'group-planning')

    planning_items = page.locator('#group-planning.group-items')
    expect(planning_items).to_be_visible()

    training_button = page.locator('button.group-header:has-text("💪 Training")')
    expect(training_button).to_have_attribute('aria-controls', 'group-training')

    # Capture a screenshot
    page.screenshot(path="verification/sidebar-accessibility.png")

if __name__ == "__main__":
    import os
    os.makedirs("verification", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_sidebar_accessibility(page)
        except Exception as e:
            page.screenshot(path="verification/error-state.png")
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            browser.close()
