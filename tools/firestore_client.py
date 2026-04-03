import os
from datetime import datetime
from google.cloud import firestore
from models.schema import Concept, ConceptLink, ForgettingState, StudentSession


class FirestoreClient:
    def __init__(self):
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.db = firestore.Client(project=project)

    # ── Concepts ──────────────────────────────────────────────

    def save_concept(self, concept: Concept, student_id: str) -> str:
        ref = (
            self.db
            .collection("students")
            .document(student_id)
            .collection("concepts")
            .document(concept.id)
        )
        ref.set(concept.model_dump())
        return concept.id

    def get_concepts(self, student_id: str) -> list[Concept]:
        docs = (
            self.db
            .collection("students")
            .document(student_id)
            .collection("concepts")
            .stream()
        )
        return [Concept(**doc.to_dict()) for doc in docs]

    def get_concept(self, student_id: str, concept_id: str) -> Concept | None:
        ref = (
            self.db
            .collection("students")
            .document(student_id)
            .collection("concepts")
            .document(concept_id)
        )
        doc = ref.get()
        return Concept(**doc.to_dict()) if doc.exists else None

    # ── Concept links ──────────────────────────────────────────

    def save_concept_link(self, link: ConceptLink, student_id: str):
        self.db.collection("students").document(student_id).collection("links").add(
            link.model_dump()
        )

    def get_concept_links(self, student_id: str) -> list[ConceptLink]:
        docs = (
            self.db
            .collection("students")
            .document(student_id)
            .collection("links")
            .stream()
        )
        return [ConceptLink(**doc.to_dict()) for doc in docs]

    # ── Forgetting state ───────────────────────────────────────

    def save_forgetting_state(self, state: ForgettingState):
        ref = (
            self.db
            .collection("students")
            .document(state.student_id)
            .collection("forgetting")
            .document(state.concept_id)
        )
        ref.set(state.model_dump())

    def get_forgetting_state(
        self, student_id: str, concept_id: str
    ) -> ForgettingState | None:
        ref = (
            self.db
            .collection("students")
            .document(student_id)
            .collection("forgetting")
            .document(concept_id)
        )
        doc = ref.get()
        return ForgettingState(**doc.to_dict()) if doc.exists else None

    def get_all_forgetting_states(self, student_id: str):
        docs = (
            self.db
            .collection("students")
            .document(student_id)
            .collection("forgetting")
            .limit(20)   # ✅ ADD THIS
            .stream()
        )
        return [ForgettingState(**doc.to_dict()) for doc in docs]

    def get_due_for_review(
        self, student_id: str, now: datetime | None = None
    ) -> list[ForgettingState]:
        now = now or datetime.utcnow()
        docs = (
            self.db
            .collection("students")
            .document(student_id)
            .collection("forgetting")
            .where("next_review_at", "<=", now)
            .stream()
        )
        return [ForgettingState(**doc.to_dict()) for doc in docs]

    # ── Sessions ───────────────────────────────────────────────

    def save_session(self, session: StudentSession):
        self.db.collection("sessions").document(session.student_id).set(
            session.model_dump()
        )

    def get_session(self, student_id: str) -> StudentSession | None:
        doc = self.db.collection("sessions").document(student_id).get()
        return StudentSession(**doc.to_dict()) if doc.exists else None
