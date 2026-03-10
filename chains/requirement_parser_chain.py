import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from chains import get_llm

SAUCEDEMO_CONTEXT = """Application: SauceDemo (https://www.saucedemo.com)
Features:
- Login page with multiple user types (standard_user, locked_out_user, problem_user, performance_glitch_user, error_user, visual_user)
- Password: secret_sauce for all users
- Products inventory page with sorting (A-Z, Z-A, price low-high, price high-low)
- Individual product detail pages
- Shopping cart (add/remove items, cart badge count)
- Checkout step 1 (first name, last name, zip code)
- Checkout step 2 (order overview/summary)
- Checkout complete page
- Navigation menu (logout, reset app state, about)"""


def _extract_json(text: str):
    """Strip markdown fences and parse JSON."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def get_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""{SAUCEDEMO_CONTEXT}

You are a QA requirements analyst. Return a JSON object with key "requirements" containing a list.
Each item must have these exact fields:
- title: short descriptive title
- description: detailed description of what needs to be tested
- feature: one of [Login, Inventory, ProductDetail, Cart, Checkout, Navigation]
- priority: one of [High, Medium, Low]
- acceptance_criteria: bullet-point acceptance criteria as a single string
- test_types: comma-separated list from [Functional, Negative, UI, Performance, Security]

Return ONLY valid JSON. No markdown fences. No extra text."""),
        ("human", "Parse these requirements:\n\n{text}"),
    ])
    return prompt | get_llm() | StrOutputParser()


def parse_requirements(text: str) -> list:
    raw = get_chain().invoke({"text": text})
    data = _extract_json(raw)
    if isinstance(data, dict) and "requirements" in data:
        return data["requirements"]
    if isinstance(data, list):
        return data
    return []
