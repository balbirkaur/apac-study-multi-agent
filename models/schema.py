from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Concept(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    topic: str
    source_document: str
    importance_score: float = 1.0  # 0.0 to 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConceptLink(BaseModel):
    from_concept_id: str
    to_concept_id: str
    relationship: str  # e.g. "prerequisite", "related", "contrast"
    strength: float = 0.5  # 0.0 to 1.0


class ForgettingState(BaseModel):
    concept_id: str
    student_id: str
    retention_score: float = 1.0       # 1.0 = fully retained, 0.0 = forgotten
    last_reviewed_at: datetime = Field(default_factory=datetime.utcnow)
    next_review_at: Optional[datetime] = None
    review_count: int = 0
    stability: float = 1.0             # Ebbinghaus stability factor (grows with reviews)
    ease_factor: float = 2.5           # SM-2 ease factor


class StudentSession(BaseModel):
    student_id: str
    document_name: str
    concepts_extracted: list[str] = []  # concept IDs
    session_started_at: datetime = Field(default_factory=datetime.utcnow)
    ingestion_complete: bool = False


class IngestionResult(BaseModel):
    session_id: str
    student_id: str
    document_name: str
    concepts: list[Concept]
    links: list[ConceptLink]
    summary: str
    total_concepts: int


class AgentResponse(BaseModel):
    agent_name: str
    success: bool
    message: str
    data: dict = {}
