from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"Page Error: {exc}"))

        # Mock dashboard data (user stats) - Required for DashboardMain
        page.route("**/api/dashboard-data", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"stats": {"id": 1, "username": "Jules", "level": 5, "current_xp": 100, "max_xp": 200, "hacksilver": 50, "strength_stat": 10, "runic_stat": 10, "vitality_stat": 10, "luck_stat": 10}, "tasks": []}'
        ))

        # Mock analytics
        page.route("**/api/analytics", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{}'
        ))

        # Mock daily challenge
        page.route("**/api/challenges/daily", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"id": 1, "title": "Playwright Challenge", "description": "Verify the UI works", "type": "test", "target_value": 10, "xp_reward": 50, "completed": false, "progress": 5}'
        ))

        # Mock streak
        page.route("**/api/challenges/streak", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"current_streak": 7}'
        ))

        # Mock complete
        page.route("**/api/challenges/complete", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"xp_awarded": 50}'
        ))

        print("Navigating to dashboard...")
        page.goto("http://localhost:5173/")

        # Wait for the card to load
        print("Waiting for challenge card...")

        try:
            expect(page.get_by_text("Playwright Challenge")).to_be_visible(timeout=10000)
        except Exception as e:
            print(f"Error finding challenge card: {e}")
            page.screenshot(path="verification/error.png")
            browser.close()
            return

        # Verify accessibility of progress bar
        print("Verifying progress bar accessibility...")
        card = page.locator(".challenge-card")
        progress_bar = card.locator(".progress-bar")

        expect(progress_bar).to_have_attribute("role", "progressbar")
        expect(progress_bar).to_have_attribute("aria-valuenow", "5")
        expect(progress_bar).to_have_attribute("aria-label", "Daily Challenge Progress")

        print("Taking initial screenshot...")
        page.screenshot(path="verification/before_complete.png")

        # Click complete
        print("Clicking Mark Complete...")
        complete_btn = page.get_by_role("button", name="Mark Complete")
        complete_btn.click()

        # Verify Toast
        print("Verifying Toast...")
        try:
            expect(page.get_by_text("Challenge completed! +50 XP")).to_be_visible(timeout=5000)
        except Exception as e:
            print(f"Toast not found: {e}")
            page.screenshot(path="verification/toast_error.png")
            browser.close()
            return

        print("Taking final screenshot...")
        page.screenshot(path="verification/after_complete.png")

        browser.close()

if __name__ == "__main__":
    run()
