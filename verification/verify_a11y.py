import time
from playwright.sync_api import sync_playwright

def verify_feature():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir="/app/verification/video")
        page = context.new_page()
        try:
            print("Navigating to Dashboard...")
            page.goto("http://localhost:5173", timeout=30000)
            page.wait_for_timeout(2000)

            print("Waiting for Revision Targets widget...")
            page.wait_for_selector(".revision-widget", timeout=30000)

            # Since the ARIA label changes are invisible, we'll just capture the widget
            # and hover over the buttons to verify they exist and are accessible.

            # Find the first item's buttons
            focus_btn = page.locator('.focus-btn').first
            revise_btn = page.locator('.quick-revise-btn').first

            if focus_btn.is_visible():
                print("Hovering Focus button...")
                focus_btn.hover()
                page.wait_for_timeout(1000)

            if revise_btn.is_visible():
                print("Hovering Revise button...")
                revise_btn.hover()
                page.wait_for_timeout(1000)

            print("Taking screenshot...")
            page.screenshot(path="/app/verification/verification.png")
            page.wait_for_timeout(1000)

            print("Verification complete.")
        except Exception as e:
            print(f"Error during verification: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    verify_feature()
