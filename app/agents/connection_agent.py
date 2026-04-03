import os
import json
from google import genai

from app.tools.firestore_client import FirestoreClient
from app.models.schema import ConceptLink


# ✅ Gemini client (NEW SDK)
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# ✅ Lazy DB (fix hanging)
def get_db():
    return FirestoreClient()


# ── PROMPTS ─────────────────────────────

BRIDGE_PROMPT = """
Find connections between isolated concepts and explain them simply.

Isolated concepts:
{isolated_concepts}

All concepts:
{all_concepts}

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

    db = get_db()   # ✅ FIX

    concepts = db.get_concepts(student_id)
    links = db.get_concept_links(student_id)

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

    # ✅ NEW SDK CALL
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

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
            db.save_concept_link(link, student_id)

    return result


def generate_analogy_for_concept(student_id: str, concept_id: str) -> dict:

    db = get_db()   # ✅ FIX

    concept = db.get_concept(student_id, concept_id)

    if not concept:
        return {"error": "Concept not found"}

    prompt = ANALOGY_PROMPT.format(
        concept_name=concept.name,
        concept_description=concept.description,
    )

    # ✅ NEW SDK CALL
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except:
        return {"error": "Failed to parse response", "raw": raw}