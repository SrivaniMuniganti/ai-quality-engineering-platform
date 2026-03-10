"""Thin wrapper so new modules import from requirement-parser.parser."""
from services.requirement_service import create_requirements_from_text


class RequirementParser:
    def parse(self, text: str) -> list[dict]:
        return create_requirements_from_text(text)
