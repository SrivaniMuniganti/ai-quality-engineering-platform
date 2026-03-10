from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from chains import get_llm

PLAYWRIGHT_CONTEXT = """You are a senior QA automation engineer writing Playwright + pytest tests for SauceDemo (https://www.saucedemo.com).

STRICT RULES — follow exactly:
1. Start with imports: import pytest, import os, from playwright.sync_api import Page
2. NEVER define a `page` fixture — it is already provided by conftest.py via sync_playwright
3. NEVER define a `logged_in_page` fixture — it is already provided by conftest.py
4. Just write test functions that accept `page` or `logged_in_page` as parameters — pytest injects them automatically
5. Use SauceDemo data-test selectors: [data-test="username"], [data-test="password"], [data-test="login-button"], [data-test="inventory-item"], [data-test="add-to-cart-sauce-labs-backpack"], etc.
6. Standard credentials: username=standard_user, password=secret_sauce. Locked out: locked_out_user / secret_sauce
7. Use SAUCEDEMO_URL = os.getenv("SAUCEDEMO_URL", "https://www.saucedemo.com")
8. Use page.goto(SAUCEDEMO_URL) inside the test function (not in a fixture)
9. Add page.wait_for_selector() / page.wait_for_url() before assertions
10. Return ONLY valid Python code, no markdown fences, no explanation

CORRECT PATTERN:
import pytest
import os
from playwright.sync_api import Page

SAUCEDEMO_URL = os.getenv("SAUCEDEMO_URL", "https://www.saucedemo.com")

def test_example(page: Page):
    page.goto(SAUCEDEMO_URL)
    page.fill('[data-test="username"]', 'standard_user')
    page.fill('[data-test="password"]', 'secret_sauce')
    page.click('[data-test="login-button"]')
    page.wait_for_url('**/inventory.html')
    assert 'inventory' in page.url"""


def get_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAYWRIGHT_CONTEXT),
        ("human", """Generate a complete Playwright + pytest script for:

Title: {title}
Feature: {feature}
Test Type: {test_type}
Preconditions: {preconditions}
Steps: {steps}
Expected Result: {expected_result}
Test Data: {test_data}

Return ONLY the Python code, starting with import statements."""),
    ])

    return prompt | get_llm() | StrOutputParser()


def _strip_conflicting_fixtures(code: str) -> str:
    """Remove any @pytest.fixture def page / logged_in_page blocks the LLM generated.
    These are already provided by conftest.py and must not be redefined."""
    import re
    # Remove fixture blocks for 'page' and 'logged_in_page'
    pattern = r'@pytest\.fixture[^\n]*\n(?:[ \t]+.*\n)*?[ \t]*def (?:page|logged_in_page)\(.*?\):[^\n]*\n(?:(?:[ \t]+.*\n?)|(?:\n))*'
    cleaned = re.sub(pattern, '', code)
    return cleaned.strip()


def generate_script(test_case: dict) -> str:
    chain = get_chain()
    raw = chain.invoke({
        "title": test_case.get("title", ""),
        "feature": test_case.get("feature", ""),
        "test_type": test_case.get("test_type", "Functional"),
        "preconditions": test_case.get("preconditions", ""),
        "steps": test_case.get("steps", ""),
        "expected_result": test_case.get("expected_result", ""),
        "test_data": test_case.get("test_data", ""),
    })
    # Strip markdown fences if LLM wrapped in them
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    # Remove any page/logged_in_page fixture redefinitions
    raw = _strip_conflicting_fixtures(raw)
    return raw
