from playwright.sync_api import sync_playwright, expect
import re

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()

    # Mock Dashboard Data
    page.route("**/api/dashboard-data", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"stats": {"level": 1, "current_xp": 100, "max_xp": 1000, "strength_stat": 10, "runic_stat": 10, "vitality_stat": 10, "luck_stat": 10}, "tasks": []}'
    ))

    # Mock Log Study (hangs)
    def handle_log_study(route):
        pass

    page.route("**/api/tasks/log-study", handle_log_study)

    print("Navigating to app...")
    page.goto("http://localhost:5173/")

    # Wait for loading to finish
    expect(page.locator(".loading-screen")).not_to_be_visible(timeout=10000)

    # Open Rituals Panel
    print("Opening Rituals Panel...")
    page.get_by_label("Toggle Rituals").click()
    expect(page.locator(".rituals-panel-wrapper")).to_have_class(re.compile(r"open"))

    # Check for Timer
    timer = page.locator(".study-timer")
    expect(timer).to_be_visible()

    # Start Timer
    print("Starting Timer...")
    page.get_by_role("button", name="Start study timer").click()

    # Wait for 61 seconds
    print("Waiting 61 seconds...")
    expect(page.locator(".timer-display")).to_contain_text("00:01:01", timeout=65000)

    # Verify Document Title
    title = page.title()
    print(f"Current Title: {title}")

    # Stop Timer (Finish)
    print("Finishing Session...")
    page.get_by_role("button", name="Finish study session and log time").click()

    # Verify Loading State
    finish_btn = page.get_by_role("button", name="Saving study session")
    expect(finish_btn).to_be_visible()
    expect(finish_btn).to_be_disabled()
    expect(finish_btn).to_have_text("SAVING...")

    print("Taking screenshot...")
    page.screenshot(path="verification/study_timer_verified.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
