import json
import re
from datetime import datetime, timezone


def extract_json(text: str) -> dict | list | None:
    """Extract first valid JSON object or array from a string."""
    for pattern in (r"\{.*\}", r"\[.*\]"):
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def safe_filename(name: str, max_len: int = 60) -> str:
    """Convert arbitrary string to a safe filename."""
    name = re.sub(r"[^\w\s-]", "", name).strip()
    name = re.sub(r"[\s]+", "_", name)
    return name[:max_len].lower()


def truncate(text: str, max_len: int = 200, suffix: str = "...") -> str:
    if not text:
        return ""
    return text if len(text) <= max_len else text[:max_len - len(suffix)] + suffix


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
