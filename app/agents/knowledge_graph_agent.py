import os
import json
import google.generativeai as genai

from app.tools.firestore_client import FirestoreClient


# ── Gemini setup (SAFE) ─────────────────────

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_model():
    """Lazy load Gemini model (prevents hanging)"""
    return genai.GenerativeModel(
        os.getenv("GEMINI_MODEL", "models/gemini-pro")
    )


# ── Firestore (SAFE) ─────────────────────

def get_db():
    return FirestoreClient()


# ── PROMPT ─────────────────────────────

GRAPH_ANALYSIS_PROMPT = """
You are an expert in learning science and concept mapping.

A student has studied these concepts:
{concepts_json}

And these relationships exist between them:
{links_json}

Analyse the knowledge graph and provide:
1. Isolated concepts
2. Prerequisite chains
3. Hub concepts
4. Missing links

Respond ONLY as valid JSON.
"""


# ── HELPER ─────────────────────────────

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


# ── MAIN FUNCTION ─────────────────────

def analyse_knowledge_graph(student_id: str) -> dict:

    db = get_db()  # ✅ FIX

    concepts = db.get_concepts(student_id)
    links = db.get_concept_links(student_id)

    if not concepts:
        return {"error": f"No concepts found for student {student_id}"}

    concepts_json = json.dumps(
        [{"id": c.id, "name": c.name, "topic": c.topic} for c in concepts],
        indent=2
    )

    links_json = json.dumps(
        [{"from": l.from_concept_id, "to": l.to_concept_id} for l in links],
        indent=2
    )

    prompt = GRAPH_ANALYSIS_PROMPT.format(
        concepts_json=concepts_json,
        links_json=links_json,
    )

    try:
        model = get_model()  # ✅ FIX
        response = model.generate_content(prompt)
        raw = response.text
    except Exception as e:
        return {"error": f"Gemini error: {str(e)}"}

    analysis = clean_json_response(raw)

    if not analysis:
        return {"error": "Failed to parse Gemini response", "raw": raw}

    analysis["total_concepts"] = len(concepts)
    analysis["total_links"] = len(links)

    return analysis