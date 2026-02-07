from playwright.sync_api import sync_playwright, expect
import datetime
import json
import traceback

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Capture console logs
    page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))
    page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))

    try:
        # Mock Dashboard Data
        page.route("**/api/dashboard-data", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "stats": {
                    "id": 1,
                    "username": "TestUser",
                    "level": 5,
                    "current_xp": 100,
                    "max_xp": 500,
                    "hacksilver": 1000,
                    "strength_stat": 10,
                    "runic_stat": 10,
                    "vitality_stat": 10,
                    "luck_stat": 10
                },
                "tasks": [
                    {
                        "id": 101,
                        "title": "Backend Task 1",
                        "isCompleted": 0,
                        "xp_reward": 50,
                        "associated_stat": "strength",
                        "due_date": datetime.date.today().isoformat()
                    }
                ]
            })
        ))

        # Mock CSV
        today_str = datetime.date.today().isoformat()
        csv_content = f"Date,Day,Week,Time,Subject,Topic,Activity,Resources\n{today_str},Friday,1,06:00,History,Ancient India,Reading,NCERT"

        page.route("**/UPSC_Scheduler.csv", lambda route: route.fulfill(
            status=200,
            content_type="text/csv",
            body=csv_content
        ))

        # Navigate to app
        page.goto("http://localhost:5174/")
        print("Navigated to http://localhost:5174/")

        # Wait for loading to finish
        print("Waiting for loading screen to disappear...")
        expect(page.locator(".loading-screen")).not_to_be_visible(timeout=10000)
        print("Loading screen disappeared.")

        # Click the right sidebar toggle
        print("Looking for Toggle Rituals button...")
        toggle_btn = page.get_by_label("Toggle Rituals")
        expect(toggle_btn).to_be_visible(timeout=5000)
        toggle_btn.click()
        print("Clicked Toggle Rituals button.")

        # Wait for panel to open
        print("Waiting for rituals panel to open...")
        expect(page.locator(".rituals-panel-wrapper")).to_have_class("rituals-panel-wrapper open")

        # Locate the checkbox for CSV task
        print("Locating CSV task checkbox...")
        csv_checkbox = page.get_by_label("Mark History - Ancient India (Reading) as completed")
        expect(csv_checkbox).to_be_attached()
        print("CSV checkbox attached.")

        # Locate the checkbox for Backend task
        print("Locating Backend task checkbox...")
        backend_checkbox = page.get_by_label("Mark Backend Task 1 as completed")
        expect(backend_checkbox).to_be_attached()
        print("Backend checkbox attached.")

        # Focus the backend checkbox to show focus ring
        print("Focusing backend checkbox...")
        backend_checkbox.focus()

        # Take screenshot
        page.screenshot(path="verification_rituals.png")
        print("Screenshot saved to verification_rituals.png")

    except Exception:
        print("Verification failed.")
        traceback.print_exc()
        page.screenshot(path="verification_failure.png")
        print("Screenshot saved to verification_failure.png")
    finally:
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
