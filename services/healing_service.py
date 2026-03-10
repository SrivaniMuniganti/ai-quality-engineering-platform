"""Orchestrates self-healing via RetryEngine and exposes DB queries."""
from core.database import get_session
from core.models import HealingAttempt
from self_healing_engine.retry_engine import RetryEngine


def attempt_self_heal(run_id: int) -> dict:
    engine = RetryEngine()
    return engine.retry_with_healing(run_id)


def get_all_healing_attempts() -> list[dict]:
    db = get_session()
    try:
        attempts = db.query(HealingAttempt).order_by(HealingAttempt.created_at.desc()).all()
        return [_to_dict(a) for a in attempts]
    finally:
        db.close()


def get_healing_stats() -> dict:
    db = get_session()
    try:
        attempts = db.query(HealingAttempt).all()
        total = len(attempts)
        healed = sum(1 for a in attempts if a.status == "healed")
        failed = sum(1 for a in attempts if a.status == "failed")
        skipped = sum(1 for a in attempts if a.status == "skipped")
        success_rate = round(healed / total * 100, 1) if total > 0 else 0.0
        avg_confidence = (
            round(sum(a.confidence_score or 0 for a in attempts) / total, 2) if total > 0 else 0.0
        )
        return {
            "total": total,
            "healed": healed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": success_rate,
            "avg_confidence": avg_confidence,
        }
    finally:
        db.close()


def _to_dict(a: HealingAttempt) -> dict:
    return {
        "id": a.id,
        "run_id": a.run_id,
        "test_name": a.test_name,
        "original_locator": a.original_locator,
        "suggested_locators": a.suggested_locators,
        "healing_strategy": a.healing_strategy,
        "status": a.status,
        "confidence_score": a.confidence_score,
        "created_at": a.created_at,
    }
