"""Collects and persists test run results to JSON log files."""
import json
import os
from datetime import datetime, timezone

from services.execution_service import get_all_runs

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)


class ResultCollector:
    def save_json_log(self, run_dict: dict) -> str:
        """Persist a single run dict as reports/logs/run_{id}.json. Returns path."""
        os.makedirs(LOGS_DIR, exist_ok=True)
        run_id = run_dict.get("id", "unknown")
        path = os.path.join(LOGS_DIR, f"run_{run_id}.json")

        serialisable = {}
        for k, v in run_dict.items():
            if hasattr(v, "isoformat"):
                serialisable[k] = v.isoformat()
            else:
                serialisable[k] = v

        serialisable["saved_at"] = datetime.now(timezone.utc).isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serialisable, f, indent=2)
        return path

    def collect_all(self) -> list[dict]:
        """Return all run records from DB."""
        return get_all_runs()
