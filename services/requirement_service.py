import json
from core.database import get_session
from core.models import Requirement
from core.security import sanitize_input
from chains.requirement_parser_chain import parse_requirements


def _coerce_str(val) -> str:
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    return str(val) if val is not None else ""


DEFAULT_REQUIREMENTS_TEXT = """
1. Users must be able to login with valid credentials (standard_user/secret_sauce)
2. Locked out users should see an error message and cannot login
3. Products page should display all 6 items with name, image, description and price
4. Products can be sorted by name (A-Z, Z-A) and price (low to high, high to low)
5. Users can add items to cart and the cart badge count should update
6. Users can remove items from cart both from product page and cart page
7. Checkout requires first name, last name and zip code - all fields mandatory
8. Order summary should show correct items, prices and total
9. After successful checkout, user sees confirmation page
10. User can logout from the hamburger menu
"""


def create_requirements_from_text(text: str) -> list:
    text = sanitize_input(text)
    parsed = parse_requirements(text)

    db = get_session()
    try:
        saved = []
        for item in parsed:
            req = Requirement(
                title=_coerce_str(item.get("title", "")),
                description=_coerce_str(item.get("description", "")),
                feature=_coerce_str(item.get("feature", "Login")),
                priority=_coerce_str(item.get("priority", "Medium")),
                acceptance_criteria=_coerce_str(item.get("acceptance_criteria", "")),
                test_types=_coerce_str(item.get("test_types", "Functional")),
                raw_input=text,
            )
            db.add(req)
            db.commit()
            db.refresh(req)
            saved.append({
                "id": req.id,
                "title": req.title,
                "description": req.description,
                "feature": req.feature,
                "priority": req.priority,
                "acceptance_criteria": req.acceptance_criteria,
                "test_types": req.test_types,
            })
        return saved
    finally:
        db.close()


def get_all_requirements() -> list:
    db = get_session()
    try:
        reqs = db.query(Requirement).order_by(Requirement.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "feature": r.feature,
                "priority": r.priority,
                "acceptance_criteria": r.acceptance_criteria,
                "test_types": r.test_types,
                "created_at": r.created_at,
            }
            for r in reqs
        ]
    finally:
        db.close()


def seed_default_requirements() -> list:
    return create_requirements_from_text(DEFAULT_REQUIREMENTS_TEXT)


def get_requirement_by_id(req_id: int) -> dict | None:
    db = get_session()
    try:
        r = db.query(Requirement).filter(Requirement.id == req_id).first()
        if not r:
            return None
        return {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "feature": r.feature,
            "priority": r.priority,
            "acceptance_criteria": r.acceptance_criteria,
            "test_types": r.test_types,
        }
    finally:
        db.close()
