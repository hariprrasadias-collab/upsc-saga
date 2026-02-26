
import os
import sys
from playwright.sync_api import sync_playwright, expect

# Add backend to path so we can potentially import models if needed,
# though for this script we mainly interact with the frontend.
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def verify_syllabus_tracker():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Set viewport to ensure sidebar doesn't cover content
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Mock API responses to prevent crashes

        # 1. Mock Dashboard Data (Global Context)
        page.route("**/api/dashboard-data", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='''{
                "stats": {
                    "id": 1,
                    "username": "Hero",
                    "current_xp": 100,
                    "level": 1,
                    "max_xp": 1000,
                    "hacksilver": 50,
                    "strength_stat": 10,
                    "runic_stat": 10,
                    "vitality_stat": 10,
                    "luck_stat": 10
                },
                "tasks": [],
                "anki_due": 0
            }'''
        ))

        # 2. Mock Syllabus Data
        # This is the critical part to verify our change.
        # We need to ensure the TopicItem renders correctly with this data.
        page.route("**/api/syllabus/", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='''[
                {
                    "id": 1,
                    "paper": "GS1",
                    "subject": "History",
                    "topic": "Ancient India",
                    "subtopic": "Indus Valley Civilization",
                    "status": "Not Started",
                    "notes": null,
                    "last_updated": "2023-01-01T00:00:00",
                    "revision_count": 0,
                    "next_revision_date": "2024-01-01"
                },
                {
                    "id": 2,
                    "paper": "GS1",
                    "subject": "History",
                    "topic": "Medieval India",
                    "subtopic": "Mughal Empire",
                    "status": "Completed",
                    "notes": "Some notes",
                    "last_updated": "2023-01-02T00:00:00",
                    "revision_count": 1,
                    "next_revision_date": "2025-01-01"
                }
            ]'''
        ))

        try:
            print("Navigating to Home page (App root)...")
            # We assume the app is running on localhost:5173
            # App.tsx only renders SyllabusTracker if currentTab === 'syllabus'
            # We need to click the Syllabus button in the sidebar.
            page.goto("http://localhost:5173/")

            # Open Sidebar explicitly first
            print("Opening Sidebar...")
            # Toggle button class: sidebar-toggle-btn
            page.click(".sidebar-toggle-btn")

            # Wait for Sidebar
            print("Waiting for Syllabus link...")
            # Assuming there is a button/link with text "Syllabus" in the sidebar
            page.wait_for_selector("text=Syllabus", timeout=10000)

            print("Clicking Syllabus in Sidebar...")
            # Force click if covered
            page.click("text=Syllabus", force=True)

            # Wait for content to load
            print("Waiting for Syllabus Tracker header...")
            page.wait_for_selector("text=Syllabus Tracker", timeout=10000)

            # The paper card "GS1" should be visible
            print("Waiting for GS1 card...")
            page.wait_for_selector("text=GS1", timeout=10000)

            # Expand History (Subject)
            print("Expanding History...")
            # The subject header has class "subject-header"
            # It might take a moment to render.
            page.wait_for_selector(".subject-header", timeout=5000)
            page.click(".subject-header")

            # Check for Topics
            print("Checking topics...")
            # "Ancient India" should be visible
            page.wait_for_selector("text=Ancient India", timeout=5000)

            # "Medieval India" should be visible
            expect(page.locator("text=Medieval India")).to_be_visible()

            # Take a screenshot
            screenshot_path = "verification/syllabus_tracker.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Verification failed: {e}")
            # Take error screenshot
            page.screenshot(path="verification/error_syllabus.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    verify_syllabus_tracker()
