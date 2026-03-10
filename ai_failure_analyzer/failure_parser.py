"""Parses raw pytest output to extract structured failure information."""
import re


class FailureParser:
    def parse(self, output: str) -> dict:
        """Extract error type, locator hint, and line number from pytest output."""
        if not output:
            return {"error_type": "Unknown", "locator": None, "line_number": None, "raw": ""}

        error_type = "Unknown"
        locator = None
        line_number = None

        # Determine error type
        if "TimeoutError" in output or "Timeout" in output:
            error_type = "TimeoutError"
        elif "ElementNotFound" in output or "strict mode violation" in output or "locator.click" in output:
            error_type = "ElementNotFound"
        elif "AssertionError" in output or "assert " in output:
            error_type = "AssertionError"
        elif "net::ERR" in output or "ConnectionError" in output:
            error_type = "NetworkError"
        elif "AuthenticationError" in output or "Login failed" in output:
            error_type = "AuthError"

        # Extract locator hint
        locator_match = re.search(
            r"(page\.(?:locator|click|fill|wait_for_selector)\(['\"]([^'\"]+)['\"])",
            output,
        )
        if locator_match:
            locator = locator_match.group(2)

        # Extract line number
        line_match = re.search(r"line (\d+)", output)
        if line_match:
            line_number = int(line_match.group(1))

        return {
            "error_type": error_type,
            "locator": locator,
            "line_number": line_number,
            "raw": output[:1000],
        }
