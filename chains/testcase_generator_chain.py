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
        ("system", """You are a senior QA engineer creating detailed test cases for SauceDemo (https://www.saucedemo.com).

Return a JSON object with key "test_cases" containing a list.
Each item must have these exact fields:
- title: descriptive test case title
- description: what this test case verifies
- test_type: one of [Functional, Negative, UI, Performance, Security]
- priority: one of [High, Medium, Low]
- preconditions: what must be true before the test runs
- steps: numbered step-by-step instructions as a single string
- expected_result: what should happen if the test passes
- test_data: specific data values to use (usernames, passwords, form values)

Return ONLY valid JSON. No markdown fences. No extra text."""),
        ("human", """Requirement:
Title: {title}
Description: {description}
Feature: {feature}
Acceptance Criteria: {acceptance_criteria}
Test Types: {test_types}

Generate thorough test cases covering all acceptance criteria and test types specified."""),
    ])
    return prompt | get_llm() | StrOutputParser()


def generate_test_cases(requirement: dict) -> list:
    raw = get_chain().invoke({
        "title": requirement.get("title", ""),
        "description": requirement.get("description", ""),
        "feature": requirement.get("feature", ""),
        "acceptance_criteria": requirement.get("acceptance_criteria", ""),
        "test_types": requirement.get("test_types", "Functional"),
    })
    data = _extract_json(raw)
    if isinstance(data, dict) and "test_cases" in data:
        return data["test_cases"]
    if isinstance(data, list):
        return data
    return []
