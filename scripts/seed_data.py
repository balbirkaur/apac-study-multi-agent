# import uuid
# import random
# from datetime import datetime, timedelta

# from tools.firestore_client import FirestoreClient
# from models.schema import Concept, ForgettingState

# db = FirestoreClient()

# student_id = "s1"

# topics = [
#     "Photosynthesis", "Respiration", "Electricity", "Force",
#     "Motion", "Light", "Sound", "Water Cycle",
#     "Human Body", "Plants", "Atoms", "Energy"
# ]

# def random_date():
#     return datetime.utcnow() - timedelta(days=random.randint(0, 10))


# for i in range(100):
#     concept_id = str(uuid.uuid4())

#     concept = Concept(
#         id=concept_id,
#         name=f"{random.choice(topics)} {i}",
#         description="Basic concept for class 6 level",
#         topic="Science",
#         source_document="seed_data"   # ✅ ADD THIS
#     )

#     db.save_concept(concept, student_id)

#     state = ForgettingState(
#         concept_id=concept_id,
#         student_id=student_id,
#         strength=random.uniform(0.5, 2.0),
#         last_reviewed_at=random_date(),
#         next_review_at=datetime.utcnow() + timedelta(days=random.randint(1, 5))
#     )

#     db.save_forgetting_state(state)

# print("✅ 100 records inserted successfully")
import uuid
import random
from datetime import datetime, timedelta

from app.tools.firestore_client import FirestoreClient
from app.models.schema import Concept, ForgettingState

db = FirestoreClient()

students = ["s1", "s2", "s3", "s4", "s5"]  # ✅ multiple students

topics = [
    "Photosynthesis", "Respiration", "Electricity", "Force",
    "Motion", "Light", "Sound", "Water Cycle",
    "Human Body", "Plants", "Atoms", "Energy"
]

def random_date():
    return datetime.utcnow() - timedelta(days=random.randint(0, 10))


for student_id in students:
    print(f"Inserting data for {student_id}...")

    for i in range(20):   # 20 concepts each → total 100 records

        concept_id = str(uuid.uuid4())

        concept = Concept(
            id=concept_id,
            name=f"{random.choice(topics)} {i}",
            description="Basic concept for class 6 level",
            topic="Science",
            source_document="seed_data"
        )

        db.save_concept(concept, student_id)

        state = ForgettingState(
            concept_id=concept_id,
            student_id=student_id,
            strength=random.uniform(0.5, 2.0),
            last_reviewed_at=random_date(),
            next_review_at=datetime.utcnow() + timedelta(days=random.randint(1, 5))
        )

        db.save_forgetting_state(state)

print("✅ Multiple students data inserted successfully")