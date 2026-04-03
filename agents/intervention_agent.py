import os
from datetime import datetime

import google.generativeai as genai

from tools.firestore_client import FirestoreClient
from tools.forgetting_curve import compute_retention, get_urgency_label


# ── Setup ─────────────────────────────

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

_model = genai.GenerativeModel(
    os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
)

_db = FirestoreClient()


# ── SAFE RETENTION (IMPORTANT) ────────

def safe_retention(state):
    strength = getattr(state, "strength", 1.0)
    last_reviewed = getattr(state, "last_reviewed_at", None)

    if last_reviewed:
        return compute_retention(last_reviewed, strength)
    return 0.5


# ── NEXT INTERVENTION ─────────────────

def get_next_intervention(student_id: str) -> dict:

    states = _db.get_all_forgetting_states(student_id)
    concepts = {c.id: c for c in _db.get_concepts(student_id)}

    if not states:
        return {"message": "No study data found"}

    scored = []

    for s in states:
        retention = safe_retention(s)
        scored.append((s, retention))

    scored.sort(key=lambda x: x[1])  # weakest first

    weakest = scored[0][0]
    concept = concepts.get(weakest.concept_id)

    return {
        "action": "review",
        "concept_id": weakest.concept_id,
        "concept_name": concept.name if concept else "Unknown",
        "reason": "This concept has the lowest retention",
        "urgency": get_urgency_label(scored[0][1])
    }


# ── DAILY SUMMARY ─────────────────────

def get_daily_summary(student_id: str) -> dict:

    states = _db.get_all_forgetting_states(student_id)
    concepts = {c.id: c for c in _db.get_concepts(student_id)}

    if not states:
        return {"message": "No data available"}

    summary = []

    for state in states:
        retention = safe_retention(state)
        concept = concepts.get(state.concept_id)

        summary.append({
            "concept_name": concept.name if concept else "Unknown",
            "retention": round(retention, 2),
            "urgency": get_urgency_label(retention)
        })

    # sort by weakest first
    summary.sort(key=lambda x: x["retention"])

    return {
        "student_id": student_id,
        "total_concepts": len(summary),
        "focus_today": summary[:3],   # top 3 weak
        "all_concepts": summary
    }


# ── REVISION PLAN ─────────────────────

def generate_revision_plan(student_id: str, days: int, hours_per_day: float) -> dict:

    states = _db.get_all_forgetting_states(student_id)
    concepts = {c.id: c for c in _db.get_concepts(student_id)}

    if not states:
        return {"error": "No data"}

    scored = []

    for s in states:
        retention = safe_retention(s)
        scored.append((s, retention))

    scored.sort(key=lambda x: x[1])

    plan = []

    total_slots = int(days * hours_per_day)

    for i in range(min(total_slots, len(scored))):
        state, retention = scored[i]
        concept = concepts.get(state.concept_id)

        plan.append({
            "day": i % days + 1,
            "concept": concept.name if concept else "Unknown",
            "retention": round(retention, 2),
            "urgency": get_urgency_label(retention)
        })

    return {
        "student_id": student_id,
        "days": days,
        "hours_per_day": hours_per_day,
        "plan": plan
    }