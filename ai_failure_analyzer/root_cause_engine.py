"""Classifies test failures into root cause categories."""

CATEGORIES = [
    "ElementNotFound",
    "TimeoutError",
    "AssertionError",
    "NetworkError",
    "AuthError",
    "ScriptError",
    "Other",
]


class RootCauseEngine:
    def classify(self, failure_output: str) -> str:
        """Return the most likely failure category for the given output."""
        if not failure_output:
            return "Other"

        text = failure_output.lower()

        if "timeout" in text:
            return "TimeoutError"
        if any(kw in text for kw in ["elementnotfound", "strict mode", "no element", "locator"]):
            return "ElementNotFound"
        if "assertionerror" in text or "assert " in text:
            return "AssertionError"
        if any(kw in text for kw in ["net::err", "connectionerror", "connection refused"]):
            return "NetworkError"
        if any(kw in text for kw in ["authenticationerror", "login failed", "incorrect credentials"]):
            return "AuthError"
        if any(kw in text for kw in ["syntaxerror", "nameerror", "typeerror", "importerror"]):
            return "ScriptError"

        return "Other"

    def severity(self, category: str) -> str:
        """Map category to severity level."""
        mapping = {
            "ElementNotFound": "High",
            "TimeoutError": "High",
            "AssertionError": "Medium",
            "NetworkError": "Critical",
            "AuthError": "Critical",
            "ScriptError": "High",
            "Other": "Low",
        }
        return mapping.get(category, "Medium")
