import os
import re

GENERATED_TESTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_tests")

INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"ignore\s+all\s+instructions",
    r"you\s+are\s+now",
    r"act\s+as\s+",
    r"jailbreak",
    r"<\s*script\s*>",
    r"javascript\s*:",
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__",
    r"os\.system",
    r"subprocess",
]

MAX_INPUT_LENGTH = 5000


def sanitize_input(text: str) -> str:
    if not text:
        return ""
    text = text[:MAX_INPUT_LENGTH]
    for pattern in INJECTION_PATTERNS:
        text = re.sub(pattern, "[REMOVED]", text, flags=re.IGNORECASE)
    return text.strip()


def validate_script_path(path: str) -> bool:
    """Ensure resolved path is inside generated_tests/ directory."""
    try:
        resolved = os.path.realpath(path)
        allowed = os.path.realpath(GENERATED_TESTS_DIR)
        return resolved.startswith(allowed)
    except Exception:
        return False


def validate_generated_script(content: str) -> bool:
    """Validate that AI-generated script starts with import/from statement."""
    stripped = content.strip()
    return stripped.startswith("import ") or stripped.startswith("from ")
