import os
from core.database import get_session
from core.models import Script
from core.security import validate_script_path, validate_generated_script
from chains.script_generator_chain import generate_script

GENERATED_TESTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_tests")


def create_script_for_test_case(requirement: dict, test_case: dict) -> dict:
    tc_with_feature = {**test_case, "feature": requirement.get("feature", "")}
    content = generate_script(tc_with_feature)

    if not validate_generated_script(content):
        raise ValueError("Generated script failed validation: must start with import/from statement")

    safe_name = "".join(
        c if c.isalnum() or c == "_" else "_"
        for c in test_case["title"].lower()
    )[:50]

    os.makedirs(GENERATED_TESTS_DIR, exist_ok=True)
    filename = f"test_{safe_name}.py"
    script_path = os.path.join(GENERATED_TESTS_DIR, filename)

    if not validate_script_path(script_path):
        raise ValueError(f"Path traversal detected: {script_path}")

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(content)

    db = get_session()
    try:
        script = Script(
            requirement_id=requirement["id"],
            test_case_id=test_case["id"],
            title=test_case["title"],
            feature=requirement.get("feature", ""),
            script_content=content,
            script_path=script_path,
        )
        db.add(script)
        db.commit()
        db.refresh(script)
        return _script_to_dict(script)
    finally:
        db.close()


def get_all_scripts() -> list:
    db = get_session()
    try:
        scripts = db.query(Script).order_by(Script.created_at.desc()).all()
        return [_script_to_dict(s) for s in scripts]
    finally:
        db.close()


def get_script_by_id(script_id: int) -> dict | None:
    db = get_session()
    try:
        s = db.query(Script).filter(Script.id == script_id).first()
        return _script_to_dict(s) if s else None
    finally:
        db.close()


def _script_to_dict(s: Script) -> dict:
    return {
        "id": s.id,
        "requirement_id": s.requirement_id,
        "test_case_id": s.test_case_id,
        "title": s.title,
        "feature": s.feature,
        "script_content": s.script_content,
        "script_path": s.script_path,
        "created_at": s.created_at,
    }
