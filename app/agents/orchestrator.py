# agents/orchestrator.py

from app.agents.ingestion_agent import ingest_document
from app.agents.knowledge_graph_agent import analyse_knowledge_graph
from app.agents.diagnostic_agent import generate_quiz_for_weakest_concept
from app.agents.connection_agent import find_and_bridge_isolated_concepts
from app.agents.intervention_agent import get_next_intervention


def handle_chat(message: str, student_id: str):
    """
    Simple orchestrator that routes user intent to the correct agent.
    """

    message = message.lower()

    # 🧠 LEARNING / INGESTION
    if "learn" in message or "study" in message:
        return ingest_document(
            student_id=student_id,
            document_name="chat_input",
            text_content=message,
        )

    # 📊 KNOWLEDGE GRAPH
    elif "graph" in message or "structure" in message:
        return analyse_knowledge_graph(student_id)

    # 🧪 QUIZ
    elif "quiz" in message or "test" in message:
        return generate_quiz_for_weakest_concept(student_id)

    # 🔗 CONNECTION / ANALOGY
    elif "connect" in message or "analogy" in message:
        return find_and_bridge_isolated_concepts(student_id)

    # 🎯 INTERVENTION / WHAT TO STUDY
    elif "what should i study" in message or "review" in message:
        return get_next_intervention(student_id)

    # 🧠 DEFAULT RESPONSE
    else:
        return {
            "message": "I can help you learn, review, or quiz. Try saying: 'learn photosynthesis' or 'quiz me'"
        }