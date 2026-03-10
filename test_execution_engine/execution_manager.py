"""Batch execution manager for running multiple scripts."""
from services.execution_service import execute_script
from services.script_service import get_all_scripts


class ExecutionManager:
    def run_all(self) -> list[dict]:
        """Execute all scripts sequentially and return results."""
        scripts = get_all_scripts()
        results = []
        for s in scripts:
            try:
                result = execute_script(s["id"])
                results.append(result)
            except Exception as e:
                results.append({"script_id": s["id"], "status": "error", "error_message": str(e)})
        return results

    def run_by_feature(self, feature: str) -> list[dict]:
        """Execute all scripts for a given feature area."""
        scripts = [s for s in get_all_scripts() if (s.get("feature") or "").lower() == feature.lower()]
        results = []
        for s in scripts:
            try:
                result = execute_script(s["id"])
                results.append(result)
            except Exception as e:
                results.append({"script_id": s["id"], "status": "error", "error_message": str(e)})
        return results
