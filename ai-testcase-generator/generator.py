"""Thin wrapper around the existing testcase_generator_chain."""
from services.testcase_service import generate_test_cases


class TestCaseGenerator:
    def generate(self, requirement_id: int) -> list[dict]:
        return generate_test_cases(requirement_id)
