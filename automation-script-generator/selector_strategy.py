from enum import Enum


class SelectorStrategy(str, Enum):
    DATA_TEST = "data-test"
    ARIA = "aria"
    CSS = "css"
    XPATH = "xpath"


# SauceDemo element selector registry
SAUCEDEMO_SELECTORS: dict[str, dict] = {
    "username_input": {
        SelectorStrategy.DATA_TEST: "[data-test='username']",
        SelectorStrategy.CSS: "#user-name",
        SelectorStrategy.XPATH: "//input[@id='user-name']",
    },
    "password_input": {
        SelectorStrategy.DATA_TEST: "[data-test='password']",
        SelectorStrategy.CSS: "#password",
        SelectorStrategy.XPATH: "//input[@id='password']",
    },
    "login_button": {
        SelectorStrategy.DATA_TEST: "[data-test='login-button']",
        SelectorStrategy.CSS: "#login-button",
        SelectorStrategy.XPATH: "//input[@id='login-button']",
    },
    "error_message": {
        SelectorStrategy.DATA_TEST: "[data-test='error']",
        SelectorStrategy.CSS: ".error-message-container",
        SelectorStrategy.XPATH: "//h3[@data-test='error']",
    },
    "inventory_list": {
        SelectorStrategy.CSS: ".inventory_list",
        SelectorStrategy.XPATH: "//div[@class='inventory_list']",
    },
    "add_to_cart_first": {
        SelectorStrategy.CSS: ".inventory_item:first-child button",
        SelectorStrategy.XPATH: "(//button[contains(@data-test,'add-to-cart')])[1]",
    },
    "cart_badge": {
        SelectorStrategy.CSS: ".shopping_cart_badge",
        SelectorStrategy.XPATH: "//span[@class='shopping_cart_badge']",
    },
    "cart_link": {
        SelectorStrategy.CSS: ".shopping_cart_link",
        SelectorStrategy.XPATH: "//a[@class='shopping_cart_link']",
    },
    "checkout_button": {
        SelectorStrategy.DATA_TEST: "[data-test='checkout']",
        SelectorStrategy.CSS: "#checkout",
    },
    "first_name": {
        SelectorStrategy.DATA_TEST: "[data-test='firstName']",
        SelectorStrategy.CSS: "#first-name",
    },
    "last_name": {
        SelectorStrategy.DATA_TEST: "[data-test='lastName']",
        SelectorStrategy.CSS: "#last-name",
    },
    "zip_code": {
        SelectorStrategy.DATA_TEST: "[data-test='postalCode']",
        SelectorStrategy.CSS: "#postal-code",
    },
    "continue_button": {
        SelectorStrategy.DATA_TEST: "[data-test='continue']",
        SelectorStrategy.CSS: "#continue",
    },
    "finish_button": {
        SelectorStrategy.DATA_TEST: "[data-test='finish']",
        SelectorStrategy.CSS: "#finish",
    },
    "order_confirmation": {
        SelectorStrategy.CSS: ".complete-header",
        SelectorStrategy.XPATH: "//h2[@class='complete-header']",
    },
    "sort_dropdown": {
        SelectorStrategy.DATA_TEST: "[data-test='product_sort_container']",
        SelectorStrategy.CSS: ".product_sort_container",
    },
    "hamburger_menu": {
        SelectorStrategy.CSS: "#react-burger-menu-btn",
        SelectorStrategy.XPATH: "//button[@id='react-burger-menu-btn']",
    },
    "logout_link": {
        SelectorStrategy.CSS: "#logout_sidebar_link",
        SelectorStrategy.XPATH: "//a[@id='logout_sidebar_link']",
    },
}


def get_selectors(element: str) -> dict:
    """Return selector candidates for a named element, primary first."""
    return SAUCEDEMO_SELECTORS.get(element, {})
