from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.on("console", lambda msg: print(f"Console: {msg.text}"))
    page.on("pageerror", lambda err: print(f"PageError: {err}"))

    try:
        page.goto("http://localhost:5173", timeout=10000)
        page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Error: {e}")

    browser.close()

with sync_playwright() as p:
    run(p)
