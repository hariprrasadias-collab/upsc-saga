from playwright.sync_api import sync_playwright

def verify_dashboard_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Intercept calls
        page.route("**/api/dashboard-data", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='''
            {
                "tasks": [],
                "stats": {
                    "level": 10,
                    "current_xp": 4500,
                    "max_xp": 5000,
                    "strength_stat": 85,
                    "runic_stat": 70,
                    "vitality_stat": 60,
                    "luck_stat": 90
                }
            }
            '''
        ))
        page.route("**/api/**", lambda route: route.fulfill(
            status=200, content_type="application/json", body='{}'
        ))

        print("Navigating to dashboard...")
        page.goto("http://localhost:5173/")

        # Wait for animation to settle (animation is 0.6s)
        print("Waiting for entry animations...")
        page.wait_for_timeout(1000)

        # Verify dashboard container is visible
        dashboard = page.locator(".dashboard-main")
        dashboard.wait_for(state="visible")

        # Check if stats panel is visible (it had delay)
        stats_panel = page.locator(".stats-panel-left")

        # Take screenshot of the enhanced dashboard
        print("Taking screenshot...")
        page.screenshot(path="verification/dashboard_polish.png")

        # Verify stats visibility by checking opacity or visibility
        # Note: Playwright's is_visible() checks display:none or visibility:hidden, not opacity=0.
        # But our animation ends with opacity:1.

        # Hover over a stat item to verify hover effect
        print("Hovering over stat item...")
        stat_item = page.locator(".stat-item").first
        stat_item.hover()
        page.wait_for_timeout(300) # Wait for transition
        page.screenshot(path="verification/stat_item_hover.png")

        browser.close()

if __name__ == "__main__":
    verify_dashboard_ui()
