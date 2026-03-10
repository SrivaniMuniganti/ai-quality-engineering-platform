"""Extracts interactive element selectors from SauceDemo using Playwright."""
from __future__ import annotations


class DOMAnalyzer:
    BASE_URL = "https://www.saucedemo.com"

    def extract_locators(
        self,
        url: str = BASE_URL,
        username: str = "standard_user",
        password: str = "secret_sauce",
    ) -> dict[str, list[str]]:
        """Browse SauceDemo and return selectors for all interactive elements.

        Returns a dict: {element_description: [selector_candidates]}.
        Falls back to a static registry if Playwright is unavailable.
        """
        try:
            return self._dynamic_extract(url, username, password)
        except Exception:
            return self._static_fallback()

    def _dynamic_extract(self, url: str, username: str, password: str) -> dict[str, list[str]]:
        from playwright.sync_api import sync_playwright

        result: dict[str, list[str]] = {}

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # --- Login page ---
            page.goto(url)
            page.wait_for_load_state("networkidle")
            result.update(self._collect_elements(page, "login"))

            # --- Inventory page ---
            page.fill("[data-test='username']", username)
            page.fill("[data-test='password']", password)
            page.click("[data-test='login-button']")
            page.wait_for_url("**/inventory.html")
            result.update(self._collect_elements(page, "inventory"))

            # --- Cart page ---
            page.click(".shopping_cart_link")
            page.wait_for_url("**/cart.html")
            result.update(self._collect_elements(page, "cart"))

            browser.close()

        return result

    def _collect_elements(self, page, context: str) -> dict[str, list[str]]:
        selectors: dict[str, list[str]] = {}
        elements = page.query_selector_all(
            "button, input, a, [data-test], [id], [class]"
        )
        for el in elements:
            try:
                tag = el.evaluate("e => e.tagName.toLowerCase()")
                el_id = el.get_attribute("id") or ""
                el_class = (el.get_attribute("class") or "").split()[0] if el.get_attribute("class") else ""
                data_test = el.get_attribute("data-test") or ""
                text = (el.inner_text() or "")[:30].strip()

                candidates = []
                if data_test:
                    candidates.append(f"[data-test='{data_test}']")
                if el_id:
                    candidates.append(f"#{el_id}")
                if el_class:
                    candidates.append(f".{el_class}")
                if text:
                    candidates.append(f"{tag}:has-text('{text}')")

                if candidates:
                    key = f"{context}_{data_test or el_id or el_class or text or tag}"
                    selectors[key] = candidates
            except Exception:
                continue
        return selectors

    def _static_fallback(self) -> dict[str, list[str]]:
        """Return a curated static selector registry when live extraction fails."""
        return {
            "login_username": ["[data-test='username']", "#user-name"],
            "login_password": ["[data-test='password']", "#password"],
            "login_button": ["[data-test='login-button']", "#login-button"],
            "login_error": ["[data-test='error']", ".error-message-container h3"],
            "inventory_list": [".inventory_list", "#inventory_container"],
            "add_to_cart": ["[data-test^='add-to-cart']", ".btn_inventory"],
            "cart_badge": [".shopping_cart_badge"],
            "cart_link": [".shopping_cart_link", "a.shopping_cart_link"],
            "checkout_btn": ["[data-test='checkout']", "#checkout"],
            "first_name": ["[data-test='firstName']", "#first-name"],
            "last_name": ["[data-test='lastName']", "#last-name"],
            "zip": ["[data-test='postalCode']", "#postal-code"],
            "continue_btn": ["[data-test='continue']", "#continue"],
            "finish_btn": ["[data-test='finish']", "#finish"],
            "order_confirm": [".complete-header", "h2.complete-header"],
            "sort_dropdown": ["[data-test='product_sort_container']", ".product_sort_container"],
            "hamburger": ["#react-burger-menu-btn", "button.bm-burger-button"],
            "logout": ["#logout_sidebar_link", "a#logout_sidebar_link"],
        }
