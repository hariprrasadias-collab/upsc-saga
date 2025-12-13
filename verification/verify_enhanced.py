from playwright.sync_api import sync_playwright

def verify_enhanced_a11y():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Intercept API calls
        page.route("**/api/**", lambda route: route.fulfill(
            status=200, content_type="application/json", body='{"tasks": [], "stats": {}, "data": []}'
        ))

        print("Navigating to dashboard...")
        page.goto("http://localhost:5173/")

        # 1. Verify Skip Link
        print("Checking Skip Link...")
        # Press Tab to focus the first element (should be skip link)
        page.keyboard.press("Tab")
        skip_link = page.locator(".skip-link")

        # It should be visible now
        if skip_link.is_visible():
            print("Skip link is visible on focus.")
            page.screenshot(path="verification/skip_link_visible.png")
        else:
            print("Skip link NOT visible on focus.")

        # 2. Verify Sidebar Aria Attributes
        print("Checking Sidebar ARIA...")

        # Check aria-current on active item (Dashboard should be active by default)
        dashboard_btn = page.locator("button.menu-item").first
        aria_current = dashboard_btn.get_attribute("aria-current")
        print(f"Dashboard aria-current: {aria_current}")

        if aria_current == "page":
            print("aria-current='page' verified.")
        else:
            print(f"aria-current check failed: {aria_current}")

        # Check aria-expanded on group header
        planning_header = page.locator("button.group-header").first
        aria_expanded = planning_header.get_attribute("aria-expanded")
        print(f"Planning Group aria-expanded: {aria_expanded}")

        # 3. Verify Command Palette ARIA
        print("Checking Command Palette...")
        # Open Command Palette with Ctrl+K
        page.keyboard.press("Control+k")

        palette_modal = page.locator(".command-palette-modal")
        palette_modal.wait_for(state="visible")

        role = palette_modal.get_attribute("role")
        aria_modal = palette_modal.get_attribute("aria-modal")
        print(f"Palette Role: {role}, Aria-Modal: {aria_modal}")

        input_el = page.locator(".command-palette-search input")
        aria_activedescendant = input_el.get_attribute("aria-activedescendant")
        print(f"Input aria-activedescendant: {aria_activedescendant}")

        page.screenshot(path="verification/command_palette_a11y.png")

        browser.close()

if __name__ == "__main__":
    verify_enhanced_a11y()
