import os
import pytest
from playwright.sync_api import sync_playwright, Page, BrowserContext

SAUCEDEMO_URL = os.getenv("SAUCEDEMO_URL", "https://www.saucedemo.com")
HEADLESS = os.getenv("HEADLESS_BROWSER", "true").lower() == "true"
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", os.path.join(os.path.dirname(__file__), "..", "reports", "screenshots"))


@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, channel="chrome")
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=None
        )
        pg = context.new_page()
        pg.set_default_timeout(30000)
        yield pg
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def logged_in_page(page: Page):
    """Page already logged in as standard_user."""
    page.goto(SAUCEDEMO_URL)
    page.fill('[data-test="username"]', 'standard_user')
    page.fill('[data-test="password"]', 'secret_sauce')
    page.click('[data-test="login-button"]')
    page.wait_for_url('**/inventory.html')
    return page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        try:
            page = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
            if page:
                os.makedirs(SCREENSHOT_DIR, exist_ok=True)
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"{item.name}.png")
                page.screenshot(path=screenshot_path)
        except Exception:
            pass
