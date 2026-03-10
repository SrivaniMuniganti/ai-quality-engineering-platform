"""Orchestrates the full self-healing flow for a failed test run."""
import re
from datetime import datetime

from core.database import get_session
from core.models import TestRun, Script, HealingAttempt
from self_healing_engine.dom_analyzer import DOMAnalyzer
from self_healing_engine.locator_healer import LocatorHealer
from services.execution_service import execute_script


class RetryEngine:
    def retry_with_healing(self, run_id: int) -> dict:
        """
        1. Fetch failed run + original script
        2. Parse broken locator from failure output
        3. Extract live DOM selectors
        4. Call LocatorHealer for alternatives
        5. Patch script with best alternative
        6. Re-execute patched script
        7. Save HealingAttempt record
        Returns healing result dict.
        """
        db = get_session()
        try:
            run = db.query(TestRun).filter(TestRun.id == run_id).first()
            if not run:
                return {"status": "failed", "error": f"Run {run_id} not found"}

            if run.status not in ("failed", "error"):
                return {"status": "skipped", "reason": "Run is not in failed/error state"}

            script = db.query(Script).filter(Script.id == run.script_id).first()
            if not script:
                return {"status": "failed", "error": "Associated script not found"}

            failure_output = run.output or run.error_message or ""

            # Extract broken locator
            broken_locator = self._extract_locator(failure_output)
            if not broken_locator:
                broken_locator = "unknown"

            # Get DOM context
            analyzer = DOMAnalyzer()
            dom_context = analyzer.extract_locators()

            # Heal
            healer = LocatorHealer()
            healing = healer.heal(broken_locator, dom_context, failure_output)
            alternatives = healing.get("alternatives", [])

            healed_script = None
            new_status = "failed"
            run_result = None

            if alternatives and script.script_path:
                # Patch script file with best alternative
                try:
                    with open(script.script_path, "r", encoding="utf-8") as f:
                        code = f.read()

                    patched = code.replace(broken_locator, alternatives[0])

                    with open(script.script_path, "w", encoding="utf-8") as f:
                        f.write(patched)

                    healed_script = patched

                    # Re-execute
                    run_result = execute_script(script.id)
                    new_status = "healed" if run_result.get("status") == "passed" else "failed"
                except Exception as e:
                    new_status = "failed"

            # Save HealingAttempt
            attempt = HealingAttempt(
                run_id=run_id,
                test_name=run.test_name,
                original_locator=broken_locator,
                suggested_locators=str(alternatives),
                healing_strategy=healing.get("strategy", "css"),
                healed_script=healed_script,
                status=new_status,
                confidence_score=healing.get("confidence", 0.0),
                created_at=datetime.utcnow(),
            )
            db.add(attempt)
            db.commit()
            db.refresh(attempt)

            return {
                "healing_attempt_id": attempt.id,
                "status": new_status,
                "original_locator": broken_locator,
                "alternatives": alternatives,
                "confidence": healing.get("confidence", 0.0),
                "strategy": healing.get("strategy"),
                "explanation": healing.get("explanation"),
                "new_run": run_result,
            }
        finally:
            db.close()

    def _extract_locator(self, output: str) -> str | None:
        """Extract the most likely broken selector from pytest output."""
        patterns = [
            r"page\.(?:locator|click|fill|wait_for_selector)\(['\"]([^'\"]+)['\"]",
            r"selector=['\"]([^'\"]+)['\"]",
            r"No element matching selector\s+['\"]([^'\"]+)['\"]",
        ]
        for pat in patterns:
            m = re.search(pat, output)
            if m:
                return m.group(1)
        return None
