"""Thin wrapper around the existing script_generator_chain."""
from services.script_service import generate_script


class PlaywrightGenerator:
    def generate(self, test_case_id: int) -> dict:
        return generate_script(test_case_id)
