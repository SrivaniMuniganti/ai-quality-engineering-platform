"""Builds exportable reports (JSON, CSV) from platform data."""
import csv
import io
import json
import os
from datetime import datetime, timezone

from services.execution_service import get_all_runs
from services.requirement_service import get_all_requirements
from services.testcase_service import get_all_test_cases
from services.script_service import get_all_scripts

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


class ReportBuilder:
    def build_json_report(self) -> dict:
        runs = get_all_runs()
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "requirements": len(get_all_requirements()),
                "test_cases": len(get_all_test_cases()),
                "scripts": len(get_all_scripts()),
                "total_runs": len(runs),
                "passed": sum(1 for r in runs if r.get("status") == "passed"),
                "failed": sum(1 for r in runs if r.get("status") == "failed"),
                "error": sum(1 for r in runs if r.get("status") == "error"),
            },
            "runs": [
                {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items()}
                for r in runs
            ],
        }

    def build_csv_report(self) -> str:
        runs = get_all_runs()
        output = io.StringIO()
        if not runs:
            return ""
        writer = csv.DictWriter(output, fieldnames=list(runs[0].keys()))
        writer.writeheader()
        for r in runs:
            row = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items()}
            writer.writerow(row)
        return output.getvalue()

    def save_report(self, fmt: str = "json") -> str:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        if fmt == "csv":
            content = self.build_csv_report()
            path = os.path.join(REPORTS_DIR, f"report_{ts}.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(content)
        else:
            content = json.dumps(self.build_json_report(), indent=2)
            path = os.path.join(REPORTS_DIR, f"report_{ts}.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        return path
