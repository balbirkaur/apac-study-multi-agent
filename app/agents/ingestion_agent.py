import os
import json
import uuid
from datetime import datetime

import google.generativeai as genai

from app.models.schema import Concept, ConceptLink, ForgettingState, IngestionResult
from app.tools.firestore_client import FirestoreClient
from app.tools.document_parser import extract_text_from_pdf, extract_text_from_string
from app.tools.forgetting_curve import compute_next_review


# ── Gemini setup (SAFE) ─────────────────────

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_model():
    """Lazy load Gemini model"""
    return genai.GenerativeModel(
        os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    )


# ── Firestore (SAFE) ─────────────────────

def get_db():
    return FirestoreClient()


# ── PROMPT (FIXED JSON ESCAPING) ───────────

EXTRACTION_PROMPT = """
Extract key learning concepts and relationships from the following text.

Return JSON:
{{
  "concepts": [
    {{"name": "...", "description": "...", "topic": "...", "importance_score": 0.9}}
  ],
  "links": [
    {{"from_concept": "...", "to_concept": "...", "relationship": "..."}}
  ],
  "summary": "..."
}}

TEXT:
{text}
"""


# ── HELPERS ─────────────────────────────

def clean_json_response(raw: str):
    if not raw:
        return None

    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except:
        return None


def _extract_concepts_with_gemini(text: str) -> dict:

    prompt = EXTRACTION_PROMPT.format(text=text[:6000])  # ✅ FIXED

    try:
        model = get_model()
        response = model.generate_content(prompt)
        raw = response.text
    except Exception as e:
        return {"concepts": [], "links": [], "summary": f"Gemini error: {str(e)}"}

    result = clean_json_response(raw)

    if not result:
        return {"concepts": [], "links": [], "summary": raw}

    return result


# ── CORE LOGIC ─────────────────────────

def ingest_document(
    student_id: str,
    document_name: str,
    file_bytes: bytes | None = None,
    text_content: str | None = None,
) -> IngestionResult:

    db = get_db()

    # 📄 Extract text
    if file_bytes:
        text = extract_text_from_pdf(file_bytes)
    elif text_content:
        text = extract_text_from_string(text_content)
    else:
        raise ValueError("Provide file or text")

    # 🤖 Gemini extraction
    extracted = _extract_concepts_with_gemini(text)

    session_id = str(uuid.uuid4())

    concept_map = {}
    saved_concepts = []
    saved_links = []

    # ── Save concepts ──
    for c in extracted.get("concepts", []):

        concept = Concept(
            name=c["name"],
            description=c.get("description", ""),
            topic=c.get("topic", "General"),
            source_document=document_name,
            importance_score=float(c.get("importance_score", 0.8)),
        )

        db.save_concept(concept, student_id)
        concept_map[concept.name] = concept.id
        saved_concepts.append(concept)

        # 🧠 Forgetting state
        state = ForgettingState(
            concept_id=concept.id,
            student_id=student_id,
            strength=1.0,
            last_reviewed_at=datetime.utcnow(),
        )

        state.next_review_at = compute_next_review(state)
        db.save_forgetting_state(state)

    # ── Save links ──
    for l in extracted.get("links", []):
        from_id = concept_map.get(l["from_concept"])
        to_id = concept_map.get(l["to_concept"])

        if from_id and to_id:
            link = ConceptLink(
                from_concept_id=from_id,
                to_concept_id=to_id,
                relationship=l.get("relationship", "related"),
                strength=float(l.get("strength", 0.5)),
            )

            db.save_concept_link(link, student_id)
            saved_links.append(link)

    return IngestionResult(
        session_id=session_id,
        student_id=student_id,
        document_name=document_name,
        concepts=saved_concepts,
        links=saved_links,
        summary=extracted.get("summary", ""),
        total_concepts=len(saved_concepts),
    )