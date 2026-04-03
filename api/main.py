import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.orchestrator import handle_chat
from agents.ingestion_agent import ingest_document
from agents.knowledge_graph_agent import analyse_knowledge_graph
from agents.diagnostic_agent import generate_quiz_for_concept, generate_quiz_for_weakest_concept, submit_quiz_answer
from agents.connection_agent import find_and_bridge_isolated_concepts, generate_analogy_for_concept
from agents.intervention_agent import get_next_intervention, generate_revision_plan, get_daily_summary

from tools.firestore_client import FirestoreClient
from tools.forgetting_curve import compute_retention, get_urgency_label

from datetime import datetime

db = FirestoreClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("MindMap API starting up...")
    yield
    print("MindMap API shutting down.")


app = FastAPI(
    title="MindMap API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health ─────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Ingest ─────────────────────────────

class TextIngestionRequest(BaseModel):
    student_id: str
    document_name: str
    content: str


@app.post("/ingest/text")
async def ingest_text(request: TextIngestionRequest):
    try:
        return ingest_document(
            student_id=request.student_id,
            document_name=request.document_name,
            text_content=request.content,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ── Graph ─────────────────────────────

@app.get("/graph/{student_id}")
async def get_graph(student_id: str):
    return analyse_knowledge_graph(student_id)


# ── Retention ─────────────────────────

@app.get("/retention/{student_id}")
async def get_retention(student_id: str):
    states = db.get_all_forgetting_states(student_id)[:10]
    concepts = {c.id: c for c in db.get_concepts(student_id)}

    dashboard = []

    for state in states:
        strength = getattr(state, "strength", 1.0)
        last_reviewed = getattr(state, "last_reviewed_at", None)

        if last_reviewed:
            retention = compute_retention(last_reviewed, strength)
        else:
            retention = 0.5

        concept = concepts.get(state.concept_id)

        dashboard.append({
            "concept_id": state.concept_id,
            "concept_name": concept.name if concept else "Unknown",
            "retention_score": round(retention, 3),
            "urgency": get_urgency_label(retention),
            "next_review_at": state.next_review_at.isoformat() if state.next_review_at else None,
        })

    dashboard.sort(key=lambda x: x["retention_score"])

    return {
        "student_id": student_id,
        "concepts": dashboard,
    }


# ── Review ────────────────────────────

@app.get("/review/{student_id}")
async def get_review(student_id: str):
    due = db.get_due_for_review(student_id)
    concepts = {c.id: c for c in db.get_concepts(student_id)}

    result = []

    for s in due:
        strength = getattr(s, "strength", 1.0)
        last_reviewed = getattr(s, "last_reviewed_at", None)

        if last_reviewed:
            retention = compute_retention(last_reviewed, strength)
        else:
            retention = 0.5

        concept = concepts.get(s.concept_id)

        result.append({
            "concept_id": s.concept_id,
            "concept_name": concept.name if concept else "Unknown",
            "retention_score": round(retention, 3),
            "urgency": get_urgency_label(retention),
        })

    return {"concepts": result}


# ── Chat ─────────────────────────────

class ChatRequest(BaseModel):
    student_id: str
    message: str


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = handle_chat(request.message, request.student_id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Quiz ─────────────────────────────

@app.get("/quiz/{student_id}/weakest")
async def weakest_quiz(student_id: str):
    return generate_quiz_for_weakest_concept(student_id)


@app.get("/quiz/{student_id}/{concept_id}")
async def concept_quiz(student_id: str, concept_id: str):
    return generate_quiz_for_concept(student_id, concept_id)


class QuizSubmission(BaseModel):
    student_id: str
    concept_id: str
    score: float


@app.post("/quiz/submit")
async def submit_quiz(submission: QuizSubmission):
    return submit_quiz_answer(
        submission.student_id,
        submission.concept_id,
        submission.score
    )


# ── Intervention ─────────────────────

@app.get("/intervention/{student_id}")
async def intervention(student_id: str):
    return get_next_intervention(student_id)


@app.get("/daily/{student_id}")
async def daily(student_id: str):
    return get_daily_summary(student_id)


class PlanRequest(BaseModel):
    student_id: str
    days_until_exam: int = 7
    hours_per_day: float = 2.0


@app.post("/plan")
async def plan(request: PlanRequest):
    return generate_revision_plan(
        request.student_id,
        request.days_until_exam,
        request.hours_per_day,
    )