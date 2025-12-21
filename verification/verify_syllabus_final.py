from playwright.sync_api import sync_playwright, expect
import time

def verify_syllabus():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Mock API responses to ensure stable data
        page.route("**/api/syllabus/", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='[{"id": 1, "paper": "GS1", "subject": "History", "topic": "Ancient India", "subtopic": null, "status": "Not Started", "notes": null, "last_updated": "2024-01-01T10:00:00"}, {"id": 2, "paper": "GS1", "subject": "History", "topic": "Medieval India", "subtopic": null, "status": "Completed", "notes": null, "last_updated": "2024-01-02T10:00:00", "next_revision_date": "2024-06-01T10:00:00"}]'
        ))

        page.route("**/api/syllabus/analytics", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"totals": [{"paper": "GS1", "total": 2}], "breakdown": [{"paper": "GS1", "status": "Not Started", "count": 1}, {"paper": "GS1", "status": "Completed", "count": 1}]}'
        ))

        page.route("**/api/dashboard-data", lambda route: route.fulfill(
             status=200,
             content_type="application/json",
             body='{"stats": {"current_xp": 100, "level": 5}, "tasks": []}'
        ))

        try:
            print("Navigating to app...")
            page.goto("http://localhost:5173/")
            time.sleep(1) # Wait for hydration

            print("Navigating to Syllabus...")
            syllabus_btn = page.get_by_role("button", name="Syllabus")
            try:
                syllabus_btn.click(timeout=5000)
            except:
                print("Standard click failed, attempting JS click...")
                syllabus_btn.evaluate("node => node.click()")

            print("Waiting for Syllabus Header...")
            expect(page.get_by_role("heading", name="Syllabus Tracker")).to_be_visible()

            print("Expanding Paper GS1...")
            # GS1 might already be expanded by default (state initialization), so we check first
            gs1_header = page.locator(".paper-header").filter(has_text="GS1")

            # If the subject list isn't visible, click to expand
            # But the code says default state is { 'GS1': true }, so it should be open.
            # However, let's verify visibility of "History" first.

            history_header = page.locator(".subject-header").filter(has_text="History")

            if not history_header.is_visible():
                print("GS1 closed? Clicking header...")
                gs1_header.click()
                expect(history_header).to_be_visible()
            else:
                print("GS1 appears open.")

            print("Expanding Subject History...")
            # Similarly, check if topic is visible before clicking
            ancient_india = page.get_by_text("Ancient India")

            if not ancient_india.is_visible():
                print("History closed? Clicking header...")
                # Force click if needed
                try:
                    history_header.click(timeout=5000)
                except:
                     history_header.evaluate("node => node.click()")

                expect(ancient_india).to_be_visible()
            else:
                print("History appears open.")

            print("Verifying Topic Items...")
            expect(ancient_india).to_be_visible()
            expect(page.get_by_text("Medieval India")).to_be_visible()

            time.sleep(1)
            output_path = "/app/verification/syllabus_optimized.png"
            page.screenshot(path=output_path)
            print(f"Screenshot taken at {output_path}")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="/app/verification/error.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    verify_syllabus()
