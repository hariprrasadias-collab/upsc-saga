from playwright.sync_api import sync_playwright, expect
import time

def verify_study_timer():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Set viewport big enough to see the rituals panel
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        # Mock dashboard data to ensure successful load
        page.route("**/api/dashboard-data", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='''{
                "stats": {
                    "id": 1,
                    "username": "TestUser",
                    "level": 5,
                    "current_xp": 100,
                    "max_xp": 1000,
                    "hacksilver": 500,
                    "strength_stat": 10,
                    "runic_stat": 10,
                    "vitality_stat": 10,
                    "luck_stat": 10
                },
                "tasks": []
            }'''
        ))

        # Mock log-study endpoint
        page.route("**/api/tasks/log-study", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"xp_earned": 50}'
        ))

        # Navigate to dashboard
        try:
            print("Navigating to dashboard...")
            page.goto("http://localhost:5173", timeout=30000)

            # Wait for dashboard to load
            print("Waiting for dashboard content...")
            page.wait_for_selector(".rituals-panel", timeout=10000)

            # Locate timer controls
            print("Locating timer...")
            start_btn = page.get_by_label("Start study timer")

            if not start_btn.is_visible():
                # Maybe using text if label not working?
                start_btn = page.get_by_text("START")

            expect(start_btn).to_be_visible()

            # Click start
            print("Starting timer...")
            start_btn.click()

            # Wait a bit
            time.sleep(1)

            # Locate finish button
            finish_btn = page.get_by_label("Finish study session and log time")
            if not finish_btn.is_visible():
                finish_btn = page.get_by_text("FINISH")

            expect(finish_btn).to_be_visible()

            # Click finish (this should trigger "too short" warning toast since < 60s)
            print("Stopping timer...")
            finish_btn.click()

            # Check for Toast
            print("Checking for toast...")
            # The toast message for short session is "Session too short to log (min 1 minute)."
            toast = page.get_by_text("Session too short to log")
            expect(toast).to_be_visible()

            # Take screenshot of the toast
            print("Taking screenshot...")
            page.screenshot(path="verification/study_timer_toast.png")
            print("Verification complete!")

        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification/error_state.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    verify_study_timer()
