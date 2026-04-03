import math
from datetime import datetime, timedelta
from app.models.schema import ForgettingState


from datetime import datetime

from datetime import datetime, timezone
import math

def compute_retention(last_reviewed_at, strength):
    # Convert Firestore timestamp → Python datetime
    if hasattr(last_reviewed_at, "to_datetime"):
        last_reviewed_at = last_reviewed_at.to_datetime()

    # Make BOTH timezone-aware
    if last_reviewed_at.tzinfo is None:
        last_reviewed_at = last_reviewed_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    elapsed_days = (now - last_reviewed_at).total_seconds() / 86400

    # forgetting curve formula
    retention = math.exp(-elapsed_days / max(strength, 0.1))

    return max(0.0, min(1.0, retention))

def compute_next_review(state: ForgettingState, target_retention: float = 0.85) -> datetime:
    """
    Solve for t when R = target_retention:
        t = -S * ln(target_retention)
    Schedule the next review at that point after last_reviewed_at.
    """
    days_until_review = -state.stability * math.log(target_retention)
    return state.last_reviewed_at + timedelta(days=days_until_review)


def update_stability_after_review(state: ForgettingState, recalled: bool) -> ForgettingState:
    """
    SM-2 inspired stability update:
    - If recalled correctly: stability grows (student is strengthening the memory)
    - If failed: stability resets to 1.0 (back to beginning)
    """
    if recalled:
        new_stability = state.stability * state.ease_factor
        new_ease = max(1.3, state.ease_factor + 0.1)
        new_review_count = state.review_count + 1
    else:
        new_stability = 1.0
        new_ease = max(1.3, state.ease_factor - 0.2)
        new_review_count = state.review_count

    now = datetime.utcnow()
    updated = state.model_copy(update={
        "stability": new_stability,
        "ease_factor": new_ease,
        "review_count": new_review_count,
        "last_reviewed_at": now,
        "retention_score": 1.0,
    })
    updated.next_review_at = compute_next_review(updated)
    return updated


def get_urgency_label(retention: float) -> str:
    if retention < 0.3:
        return "critical"
    elif retention < 0.6:
        return "due_soon"
    elif retention < 0.85:
        return "upcoming"
    else:
        return "strong"
