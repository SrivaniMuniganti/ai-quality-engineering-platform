"""Playwright pytest fixture and import template strings."""

IMPORTS_TEMPLATE = """\
import pytest
from playwright.sync_api import Page, expect
import os
"""

FIXTURE_TEMPLATE = """\
@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def logged_in_page(page):
    page.goto("https://www.saucedemo.com")
    page.fill("[data-test='username']", "standard_user")
    page.fill("[data-test='password']", "secret_sauce")
    page.click("[data-test='login-button']")
    page.wait_for_url("**/inventory.html")
    return page
"""

SCREENSHOT_HELPER = """\
def _screenshot(page, name):
    screenshot_dir = os.environ.get("SCREENSHOT_DIR", "reports/screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    page.screenshot(path=os.path.join(screenshot_dir, f"{name}.png"))
"""

CONFTEST_TEMPLATE = """\
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser():
    headless = os.environ.get("HEADLESS_BROWSER", "true").lower() != "false"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        yield browser
        browser.close()
"""
