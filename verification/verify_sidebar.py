from playwright.sync_api import sync_playwright

def verify_sidebar_accessibility():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a larger viewport to ensure sidebar is visible
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Intercept calls to avoid crashes due to missing backend
        page.route("**/api/dashboard-data", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"tasks": [], "stats": {}}'
        ))
        page.route("**/api/syllabus", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"data": []}'
        ))
        page.route("**/api/**", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{}'
        ))

        print("Navigating to dashboard...")
        page.goto("http://localhost:5173/")

        # Check if sidebar is closed, if so, toggle it
        print("Checking sidebar state...")
        # The app has a button with class .sidebar-toggle-btn

        # Wait for the toggle button to be visible
        toggle_btn = page.locator(".sidebar-toggle-btn").first
        toggle_btn.wait_for(state="visible")

        # Check if sidebar is currently closed (has 'closed' class or width 0)
        sidebar = page.locator(".sidebar")

        # If the sidebar is not visible or has width 0, click the toggle
        # The sidebar might exist in DOM but be hidden via CSS class 'closed'
        # We can check the class attribute
        sidebar_class = sidebar.get_attribute("class")
        print(f"Sidebar class: {sidebar_class}")

        if "closed" in sidebar_class:
            print("Sidebar is closed. Clicking toggle button...")
            toggle_btn.click()
            # Wait for animation
            page.wait_for_timeout(1000)

        # Wait for sidebar to be fully open
        print("Waiting for sidebar to be visible...")
        # We can wait for it not to have the 'closed' class
        page.wait_for_function("!document.querySelector('.sidebar').classList.contains('closed')")

        # Focus the first menu item (Dashboard)
        print("Focusing dashboard button...")
        dashboard_btn = page.locator("button.menu-item").first
        dashboard_btn.focus()

        # Take screenshot of focused state
        print("Taking screenshot 1 (focus dashboard)...")
        page.screenshot(path="verification/sidebar_focus.png")

        # Expand a group (Planning)
        print("Clicking Planning group header...")
        planning_header = page.locator("button.group-header").first
        planning_header.click()

        # Wait for animation - make it longer to ensure DOM update
        page.wait_for_timeout(1000)

        # Take screenshot of expanded group
        print("Taking screenshot 2 (expanded)...")
        page.screenshot(path="verification/sidebar_expanded.png")

        # In my script I was waiting for button.sub-item, but in the code it's button.menu-item.sub-item
        # I'll just look for any button that is a sub-item.
        # It's possible the click didn't expand the group if it was already expanded?
        # In Sidebar.tsx: planning: true (default expanded).
        # So clicking it collapses it!

        # If planning is already expanded, clicking it will collapse it.
        # I should check if it's expanded before clicking, or just use the default state.
        # Since 'planning' defaults to true, I should just interact with its children without clicking header.

        # Let's try to find a sub-item directly first.
        print("Looking for sub-items...")
        sub_items = page.locator("button.sub-item")
        count = sub_items.count()
        print(f"Found {count} sub-items initially.")

        if count > 0:
             sub_item = sub_items.first
             sub_item.focus()
        else:
             print("No sub-items found. Clicking header to expand...")
             planning_header.click()
             page.wait_for_timeout(500)
             sub_item = page.locator("button.sub-item").first
             sub_item.focus()

        # Take screenshot of sub-item focus
        print("Taking screenshot 3 (focus sub-item)...")
        page.screenshot(path="verification/sidebar_sub_focus.png")

        browser.close()

if __name__ == "__main__":
    verify_sidebar_accessibility()
