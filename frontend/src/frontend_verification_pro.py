
import time
from playwright.sync_api import sync_playwright

def verify_brain_vault_pro_features():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1600, 'height': 1000})
        page = context.new_page()

        # Debug network
        page.on("request", lambda request: print(f"Request: {request.method} {request.url}"))
        page.on("requestfailed", lambda request: print(f"Request Failed: {request.url}"))

        # Mock APIs - Explicitly handle the 5000 port if that's what the app uses
        def handle_dashboard(route):
            print("Fulfilling Dashboard Data")
            route.fulfill(
                status=200,
                headers={"Access-Control-Allow-Origin": "*"},
                content_type="application/json",
                body='{"stats": {"streak": 5, "xp": 1200, "level": 3, "hacksilver": 500, "badges": [], "strength_stat": 10, "runic_stat": 5, "vitality_stat": 8, "luck_stat": 3, "max_xp": 2000, "current_xp": 1200}, "tasks": []}'
            )

        def handle_content(route):
            print("Fulfilling Brain Vault Content")
            route.fulfill(
                status=200,
                headers={"Access-Control-Allow-Origin": "*"},
                content_type="application/json",
                body='''
                [
                    {
                        "id": 1,
                        "topic": "Ancient India Visualization",
                        "content_type": "VISUAL_PROMPT",
                        "content": "A detailed painting of Mohenjo Daro",
                        "created_at": "2023-10-27T10:00:00"
                    }
                ]
                '''
            )

        # Handle all API requests globally
        page.route("**/*api/dashboard-data", handle_dashboard)
        page.route("**/*api/automation/content*", handle_content)
        page.route("**/*api/syllabus", lambda r: r.fulfill(status=200, body='{"name": "root", "children": []}'))

        try:
            print("Navigating to App...")
            page.goto("http://localhost:5173")

            # Wait for any content
            page.wait_for_selector("#root", timeout=5000)

            # Force open sidebar if needed
            if page.locator(".sidebar.closed").is_visible():
                print("Sidebar closed, opening...")
                page.click(".sidebar-toggle-btn")

            # Navigate to Brain Vault
            print("Navigating to Brain Vault...")
            # Try direct navigation by text if structure is complex
            page.get_by_text("Knowledge").click()
            page.get_by_text("Brain Vault").click()

            # Wait for content
            print("Waiting for artifacts...")
            page.wait_for_selector(".vault-item", timeout=15000)

            # Open Item
            print("Opening Item...")
            page.click(".vault-item")

            # Wait for Renderer
            page.wait_for_selector(".visual-prompt-container", timeout=5000)

            print("Testing Grid Mode...")
            page.click("button[title='Compare Models (Grid)']")

            print("Testing Presets...")
            page.click("button:has-text('Presets')")
            page.fill("input[placeholder='New Preset Name...']", "MyTestPreset")
            page.click("button:has-text('Save')")

            print("Taking screenshot...")
            page.screenshot(path="/home/jules/verification/brain_vault_pro_final.png")
            print("Verification Complete!")

        except Exception as e:
            print(f"Verification Failed: {e}")
            page.screenshot(path="/home/jules/verification/error_final.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_brain_vault_pro_features()
