import os
import json
import google.generativeai as genai

from tools.firestore_client import FirestoreClient
from models.schema import ConceptLink


# ✅ Gemini setup
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
_model = genai.GenerativeModel(
    os.getenv("GEMINI_MODEL", "gemini-3-flash-PREVIEW")
)

_db = FirestoreClient()


# ── PROMPTS ─────────────────────────────

BRIDGE_PROMPT = """
Find connections between isolated concepts and explain them simply.

Return JSON:
{
  "bridges": [
    {
      "from_concept": "...",
      "to_concept": "...",
      "relationship": "...",
      "bridge_explanation": "...",
      "analogy": "..."
    }
  ]
}
"""

ANALOGY_PROMPT = """
Explain this concept using a simple analogy.

Concept: {concept_name}
Description: {concept_description}

Return JSON.
"""


# ── CORE FUNCTIONS ─────────────────────

def find_and_bridge_isolated_concepts(student_id: str) -> dict:

    concepts = _db.get_concepts(student_id)
    links = _db.get_concept_links(student_id)

    if not concepts:
        return {"error": "No concepts found"}

    linked_ids = set()
    for l in links:
        linked_ids.add(l.from_concept_id)
        linked_ids.add(l.to_concept_id)

    isolated = [c for c in concepts if c.id not in linked_ids]

    if not isolated:
        return {"message": "All concepts are connected"}

    prompt = BRIDGE_PROMPT.format(
        isolated_concepts=json.dumps([c.name for c in isolated]),
        all_concepts=json.dumps([c.name for c in concepts]),
    )

    response = _model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        result = json.loads(raw)
    except:
        return {"error": "Failed to parse AI response", "raw": raw}

    # save links
    concept_map = {c.name: c.id for c in concepts}

    for b in result.get("bridges", []):
        from_id = concept_map.get(b["from_concept"])
        to_id = concept_map.get(b["to_concept"])

        if from_id and to_id:
            link = ConceptLink(
                from_concept_id=from_id,
                to_concept_id=to_id,
                relationship=b.get("relationship", "related"),
                strength=0.6,
            )
            _db.save_concept_link(link, student_id)

    return result


def generate_analogy_for_concept(student_id: str, concept_id: str) -> dict:

    concept = _db.get_concept(student_id, concept_id)

    if not concept:
        return {"error": "Concept not found"}

    prompt = ANALOGY_PROMPT.format(
        concept_name=concept.name,
        concept_description=concept.description,
    )

    response = _model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except:
        return {"error": "Failed to parse response", "raw": raw}