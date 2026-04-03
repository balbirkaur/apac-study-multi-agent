import os
import json
from datetime import datetime

import google.generativeai as genai

from tools.firestore_client import FirestoreClient
from tools.forgetting_curve import compute_retention, update_stability_after_review


# ── Gemini setup ─────────────────────

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

_model = genai.GenerativeModel(
    os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # ✅ fixed model
)

_db = FirestoreClient()


# ── PROMPT ───────────────────────────

QUIZ_PROMPT = """
Generate 3 MCQ questions for this concept:

Concept: {concept_name}
Description: {concept_description}
Retention: {retention}

Return JSON:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }}
  ]
}}
"""


# ── HELPERS ──────────────────────────

def safe_retention(state):
    """Safely compute retention even if fields are missing"""
    strength = getattr(state, "strength", 1.0)
    last_reviewed = getattr(state, "last_reviewed_at", None)

    if last_reviewed:
        return compute_retention(last_reviewed, strength)
    return 0.5


# ── QUIZ FOR SINGLE CONCEPT ──────────

def generate_quiz_for_concept(student_id: str, concept_id: str) -> dict:

    concept = _db.get_concept(student_id, concept_id)
    if not concept:
        return {"error": "Concept not found"}

    state = _db.get_forgetting_state(student_id, concept_id)
    if not state:
        return {"error": "No forgetting state"}

    retention = safe_retention(state)

    prompt = QUIZ_PROMPT.format(
        concept_name=concept.name,
        concept_description=concept.description,
        retention=round(retention, 2),
    )

    response = _model.generate_content(prompt)
    raw = response.text.strip()

    # clean markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        quiz = json.loads(raw)
    except Exception as e:
        return {"error": "Failed to parse quiz", "raw": raw}

    quiz["concept"] = concept.name
    quiz["retention"] = retention

    return quiz


# ── QUIZ FOR WEAKEST CONCEPT ─────────

def generate_quiz_for_weakest_concept(student_id: str) -> dict:

    states = _db.get_all_forgetting_states(student_id)

    if not states:
        return {"error": "No concepts available"}

    scored = []

    for s in states:
        retention = safe_retention(s)
        scored.append((s, retention))

    # sort by weakest retention
    scored.sort(key=lambda x: x[1])

    weakest_state = scored[0][0]

    return generate_quiz_for_concept(student_id, weakest_state.concept_id)


# ── SUBMIT QUIZ RESULT ───────────────

def submit_quiz_answer(student_id: str, concept_id: str, score: float) -> dict:

    state = _db.get_forgetting_state(student_id, concept_id)

    if not state:
        return {"error": "State not found"}

    recalled = score >= 0.7

    updated = update_stability_after_review(state, recalled)

    _db.save_forgetting_state(updated)

    return {
        "concept_id": concept_id,
        "score": score,
        "recalled": recalled,
        "next_review": updated.next_review_at.isoformat() if updated.next_review_at else None,
        "message": "Good job!" if recalled else "Needs more practice"
    }