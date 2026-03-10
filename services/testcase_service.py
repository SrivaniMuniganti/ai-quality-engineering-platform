import json
from core.database import get_session
from core.models import TestCase
from chains.testcase_generator_chain import generate_test_cases


def _coerce_str(val) -> str:
    """Convert any LLM value (str, dict, list) to a plain string for DB storage."""
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    return str(val) if val is not None else ""


def create_test_cases_for_requirement(requirement: dict) -> list:
    generated = generate_test_cases(requirement)

    db = get_session()
    try:
        saved = []
        for item in generated:
            tc = TestCase(
                requirement_id=requirement["id"],
                title=_coerce_str(item.get("title", "")),
                description=_coerce_str(item.get("description", "")),
                feature=requirement.get("feature", ""),
                test_type=_coerce_str(item.get("test_type", "Functional")),
                priority=_coerce_str(item.get("priority", "Medium")),
                preconditions=_coerce_str(item.get("preconditions", "")),
                steps=_coerce_str(item.get("steps", "")),
                expected_result=_coerce_str(item.get("expected_result", "")),
                test_data=_coerce_str(item.get("test_data", "")),
            )
            db.add(tc)
            db.commit()
            db.refresh(tc)
            saved.append(_tc_to_dict(tc))
        return saved
    finally:
        db.close()


def get_test_cases_by_requirement(req_id: int) -> list:
    db = get_session()
    try:
        tcs = db.query(TestCase).filter(TestCase.requirement_id == req_id).all()
        return [_tc_to_dict(tc) for tc in tcs]
    finally:
        db.close()


def get_all_test_cases() -> list:
    db = get_session()
    try:
        tcs = db.query(TestCase).order_by(TestCase.created_at.desc()).all()
        return [_tc_to_dict(tc) for tc in tcs]
    finally:
        db.close()


def get_test_case_by_id(tc_id: int) -> dict | None:
    db = get_session()
    try:
        tc = db.query(TestCase).filter(TestCase.id == tc_id).first()
        return _tc_to_dict(tc) if tc else None
    finally:
        db.close()


def _tc_to_dict(tc: TestCase) -> dict:
    return {
        "id": tc.id,
        "requirement_id": tc.requirement_id,
        "title": tc.title,
        "description": tc.description,
        "feature": tc.feature,
        "test_type": tc.test_type,
        "priority": tc.priority,
        "preconditions": tc.preconditions,
        "steps": tc.steps,
        "expected_result": tc.expected_result,
        "test_data": tc.test_data,
        "created_at": tc.created_at,
    }
