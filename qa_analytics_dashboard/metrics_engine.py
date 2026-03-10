"""Computes quality metrics for the dashboard."""
from __future__ import annotations
import pandas as pd


class MetricsEngine:
    def compute_quality_score(
        self,
        runs: list[dict],
        analyses: list[dict],
        healing: list[dict],
    ) -> float:
        """
        Quality Score (0–100):
          pass_rate       * 0.50
          heal_success    * 0.20
          coverage_score  * 0.30
        """
        total = len(runs)
        passed = sum(1 for r in runs if r.get("status") == "passed")
        pass_rate = passed / total if total > 0 else 0.0

        healed = [h for h in healing if h.get("status") == "healed"]
        heal_success = len(healed) / len(healing) if healing else 0.0

        # Coverage: ratio of runs to analyses (proxy for how many failures were investigated)
        coverage_score = min(len(analyses) / max(total, 1), 1.0)

        score = (pass_rate * 0.50 + heal_success * 0.20 + coverage_score * 0.30) * 100
        return round(score, 1)

    def get_failure_distribution(self, analyses: list[dict]) -> dict[str, int]:
        dist: dict[str, int] = {}
        for a in analyses:
            cat = a.get("failure_category") or "Other"
            dist[cat] = dist.get(cat, 0) + 1
        return dist

    def get_execution_trend(self, runs: list[dict]) -> pd.DataFrame:
        """Returns a DataFrame with columns: date, passed, failed, error."""
        if not runs:
            return pd.DataFrame(columns=["date", "passed", "failed", "error"])

        records: dict[str, dict] = {}
        for r in runs:
            started = r.get("started_at")
            if started is None:
                continue
            if hasattr(started, "date"):
                date_key = str(started.date())
            else:
                date_key = str(started)[:10]

            if date_key not in records:
                records[date_key] = {"date": date_key, "passed": 0, "failed": 0, "error": 0}
            status = r.get("status", "error")
            if status in ("passed", "failed", "error"):
                records[date_key][status] += 1

        df = pd.DataFrame(sorted(records.values(), key=lambda x: x["date"]))
        return df

    def get_pass_rate(self, runs: list[dict]) -> float:
        total = len(runs)
        if total == 0:
            return 0.0
        passed = sum(1 for r in runs if r.get("status") == "passed")
        return round(passed / total * 100, 1)
