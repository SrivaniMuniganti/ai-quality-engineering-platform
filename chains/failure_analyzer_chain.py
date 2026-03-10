import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from chains import get_llm


def _extract_json(text: str):
    """Strip markdown fences and parse JSON."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def get_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior QA automation engineer specializing in test failure analysis for Playwright + pytest tests against SauceDemo (https://www.saucedemo.com).

Analyze the test failure and return a JSON object with these exact fields:
- root_cause: clear explanation of what caused the failure (1-3 sentences)
- failure_category: one of [ElementNotFound, TimeoutError, AssertionError, NetworkError, AuthenticationError, ScriptError, EnvironmentError]
- suggested_fix: step-by-step fix instructions as a string
- fixed_script: if the provided script has bugs, return the corrected complete Python script as a string. Otherwise return null.
- severity: one of [Critical, High, Medium, Low] based on impact

Return ONLY valid JSON. No markdown fences. No extra text."""),
        ("human", """Test Name: {test_name}

Failure Output:
{failure_output}

{script_section}"""),
    ])
    return prompt | get_llm() | StrOutputParser()


def analyze_failure(test_name: str, failure_output: str, script_content: str = "") -> dict:
    script_section = ""
    if script_content:
        script_section = f"Original Script:\n```python\n{script_content[:2000]}\n```"

    raw = get_chain().invoke({
        "test_name": test_name,
        "failure_output": failure_output[:3000],
        "script_section": script_section,
    })
    return _extract_json(raw)
