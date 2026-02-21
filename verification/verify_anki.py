import sys
import os
import re
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to home page...")
        try:
            page.goto("http://localhost:3000", timeout=60000)
        except Exception as e:
            print(f"Error navigating: {e}")
            sys.exit(1)

        # Wait for Sidebar to load
        print("Waiting for Sidebar...")
        try:
            page.wait_for_selector(".sidebar", state="attached", timeout=30000)
        except Exception as e:
            print("Sidebar not found. Dumping HTML...")
            with open("verification/sidebar_fail.html", "w") as f:
                f.write(page.content())
            page.screenshot(path="verification/sidebar_fail.png")
            sys.exit(1)

        # Open sidebar if closed
        sidebar = page.locator(".sidebar")
        classes = sidebar.get_attribute("class") or ""
        if "closed" in classes:
            print("Sidebar is closed. Opening...")
            page.click(".sidebar-toggle-btn")
            # Wait for animation
            page.wait_for_timeout(1000)

        # Expand Training group
        print("Expanding 'Training' group...")
        try:
            # Use text locator for the group header
            group_header = page.locator("button.group-header", has_text="Training")
            # Check if already expanded
            expanded = group_header.get_attribute("aria-expanded")
            if expanded != "true":
                group_header.click()
                page.wait_for_timeout(500)
        except Exception as e:
            print(f"Error expanding Training group: {e}")
            sys.exit(1)

        # Click on 'Anki Dojo'
        print("Clicking 'Anki Dojo' link...")
        try:
            link = page.locator("button.menu-item", has_text="Anki Dojo")
            if link.count() > 0:
                link.first.click()
            else:
                print("Anki Dojo link not found")
                # Dump for debug
                with open("verification/sidebar_expanded.html", "w") as f:
                    f.write(page.content())
                sys.exit(1)
        except Exception as e:
            print(f"Error clicking Anki Dojo: {e}")
            sys.exit(1)

        # Wait for Anki Dojo to appear
        print("Waiting for Anki Dojo card...")
        try:
            # Look for the flip card container
            card = page.locator(".flip-card")
            card.wait_for(state="visible", timeout=10000)
        except Exception as e:
            print("Anki Dojo card not found")
            page.screenshot(path="verification/anki_dojo_fail.png")
            sys.exit(1)

        # Verify front of card is visible
        print("Verifying front of card...")
        front = page.locator(".flip-card-front")
        # We check visibility. Note: strict mode might be an issue if multiple cards exist, but usually one main one.
        if not front.first.is_visible():
             print("Error: Front of card not visible initially")
             sys.exit(1)

        # Ensure focus is not on the Sidebar button (which blocks Space)
        # Click on the background or the progress container to blur
        print("Clicking background to blur focus...")
        page.click(".progress-container")

        # Press Space to flip
        print("Pressing Space to flip...")
        page.keyboard.press("Space")

        # Wait for back to be visible
        print("Verifying back of card...")
        # CSS transition might take a moment
        page.wait_for_timeout(1000)

        # Check if flipped class is applied on the container
        card_el = page.locator(".flip-card").first
        classes = card_el.get_attribute("class")
        print(f"Classes after flip: {classes}")

        if "flipped" not in classes:
             print("Error: Card did not flip after Space")
             # debugging screenshot
             page.screenshot(path="verification/anki_flip_fail.png")
             sys.exit(1)

        # Rate the card (press 3)
        print("Pressing '3' to rate...")
        page.keyboard.press("3")

        # Wait for next card (animation)
        page.wait_for_timeout(1000)

        # Verify we are on a new card (flipped state should be reset)
        classes_after = card_el.get_attribute("class")
        print(f"Classes after rating: {classes_after}")

        if "flipped" in classes_after:
             print("Error: Card did not reset flip state after rating")
             sys.exit(1)

        print("SUCCESS: AnkiDojo keyboard interaction verified.")
        browser.close()

if __name__ == "__main__":
    run()
