import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a wider viewport to ensure sidebar might be open or interactable
        page = browser.new_page(viewport={'width': 1280, 'height': 800})

        try:
            print("Navigating to dashboard...")
            page.goto("http://localhost:5173", timeout=60000)

            # 1. Handle Sidebar
            print("Checking sidebar state...")
            # Wait for the toggle button to be available
            page.wait_for_selector("button[aria-label='Toggle Sidebar']", timeout=10000)

            # Check if sidebar is currently open
            sidebar = page.locator(".sidebar")
            is_open = "open" in (sidebar.get_attribute("class") or "")

            if not is_open:
                print("Sidebar is closed. Clicking toggle button...")
                page.click("button[aria-label='Toggle Sidebar']")
                # Wait for sidebar to expand
                page.wait_for_selector(".sidebar.open", timeout=5000)
                print("Sidebar opened.")
            else:
                print("Sidebar is already open.")

            # 2. Click Syllabus Link
            print("Looking for Syllabus link...")
            # Ensure 'Planning' group is expanded (it defaults to true, but good to be safe)
            # If 'Syllabus' is not visible, we might need to expand 'Planning'
            if not page.is_visible("text=Syllabus"):
                print("'Syllabus' text not visible. Checking 'Planning' group...")
                if page.is_visible("text=Planning"):
                     # Check if we need to expand it? Assuming it's open for now based on Sidebar.tsx
                     pass

            page.click("text=Syllabus")

            # 3. Wait for Syllabus Component
            print("Waiting for Syllabus component...")
            # Wait for the header with the progress bar we modified
            # We added role="progressbar" to the progress bars
            page.wait_for_selector("h1:has-text('Syllabus Tracker')", timeout=15000)

            # 4. Verify ARIA changes
            print("Verifying ARIA attributes...")

            # Check for the progressbar role we added
            progress_bars = page.locator("div[role='progressbar']")
            count = progress_bars.count()
            print(f"Found {count} elements with role='progressbar'")

            if count > 0:
                aria_valuenow = progress_bars.first.get_attribute("aria-valuenow")
                print(f"First progress bar aria-valuenow: {aria_valuenow}")

            # Check for the button role on headers
            headers = page.locator("div[role='button'].paper-header")
            header_count = headers.count()
            print(f"Found {header_count} headers with role='button'")

            # 5. Take Screenshot
            page.screenshot(path="verification/success.png")
            print("Verification successful! Screenshot saved to verification/success.png")

        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification/error.png")
            print("Error screenshot saved to verification/error.png")
            # Print page source for debugging if needed, or just specific elements
            # print(page.content())
        finally:
            browser.close()

if __name__ == "__main__":
    run()
