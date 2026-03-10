"""LLM-powered failure diagnosis wrapper."""
from chains.failure_analyzer_chain import analyze_failure


class LLMDiagnosis:
    def diagnose(self, run_id: int) -> dict:
        return analyze_failure(run_id)
