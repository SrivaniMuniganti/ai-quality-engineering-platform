"""Thin wrapper around execution_service for single-script execution."""
from services.execution_service import execute_script


class TestRunner:
    def run(self, script_id: int) -> dict:
        return execute_script(script_id)
