# 🧠 MindMap – AI Study Productivity Assistant

> AI + Memory Science = Smarter Learning

---

## 🚀 Live Demo

- 🌐 **Cloud Run API**: https://mindmap-573620545233.asia-south1.run.app
- 📘 **Swagger UI**: https://mindmap-573620545233.asia-south1.run.app/docs
- 💻 **GitHub Repo**: https://github.com/balbirkaur/apac-study-multi-agent

---

## 🎯 Problem

Students forget what they study because:

- 📉 No retention tracking
- ❌ No intelligent revision system
- 📋 Static study plans ignore memory science

> Research shows: **50% of learning is forgotten within 24 hours without revision**

---

## 💡 Solution – MindMap

MindMap uses:

- 🧠 Forgetting Curve Algorithm
- 🤖 Multi-Agent AI System
- 📊 Retention Tracking

To:

- Identify weak concepts
- Generate adaptive quizzes
- Create personalized study plans

---

## 🏗️ Architecture

```
User → FastAPI → Orchestrator → Agents → Firestore → Gemini AI
```

### 🔹 Agents

- 📥 **Ingestion Agent** → Extracts concepts
- 🧠 **Knowledge Graph Agent** → Builds relationships
- 🔗 **Connection Agent** → Links isolated concepts
- 🧪 **Diagnostic Agent** → Generates quizzes
- 📅 **Intervention Agent** → Creates study plans

---

## ⚙️ Tech Stack

| Layer      | Technology        |
| ---------- | ----------------- |
| Backend    | FastAPI           |
| AI         | Google Gemini API |
| Database   | Firestore         |
| Deployment | Google Cloud Run  |
| Container  | Docker            |

---

## 📡 API Endpoints

| Method | Endpoint                     | Description          |
| ------ | ---------------------------- | -------------------- |
| POST   | `/ingest/text`               | Ingest study content |
| GET    | `/retention/{student_id}`    | Retention dashboard  |
| GET    | `/quiz/{student_id}/weakest` | Generate quiz        |
| GET    | `/daily/{student_id}`        | Daily study plan     |
| GET    | `/graph/{student_id}`        | Knowledge graph      |
| GET    | `/intervention/{student_id}` | Next action          |
| POST   | `/quiz/submit`               | Submit quiz          |
| POST   | `/chat`                      | AI assistant         |

---

## 🔗 Live Demo Flow

Try the system in this order:

1. **POST /ingest/text**
2. **GET /retention/{student_id}**
3. **GET /quiz/{student_id}/weakest**
4. **POST /quiz/submit**
5. **GET /daily/{student_id}**

This demonstrates the full learning cycle from input → retention → improvement.

---

## 🔄 How It Works

1. User uploads study content
2. AI extracts concepts & relationships
3. Knowledge graph is created
4. Retention is calculated using forgetting curve
5. Weak concepts are identified
6. AI generates adaptive quiz
7. System updates learning model
8. Personalized revision plan is generated

---

## ✨ Key Features

- ✅ Multi-Agent AI Architecture
- ✅ AI-powered concept extraction
- ✅ Forgetting curve-based retention tracking
- ✅ Adaptive quiz generation
- ✅ Personalized study plans
- ✅ Cloud-native deployment

---

## 🧠 Why MindMap is Unique

- Uses **cognitive science (forgetting curve)**, not just AI
- Multi-agent system instead of single model
- Focuses on **memory retention**, not just content generation
- Fully deployed and scalable

---

## 🧪 Example API Usage

### 📥 Ingest Notes

```json
{
  "student_id": "s1",
  "document_name": "biology",
  "content": "Photosynthesis is the process..."
}
```

---

### ❓ Generate Quiz

```
GET /quiz/s1/weakest
```

---

### 📅 Daily Plan

```
GET /daily/s1
```

---

## 📸 Screenshots

> Add your Swagger UI screenshot here

```
/docs/swagger.png
```

---

## ⚡ Performance

- FastAPI async APIs
- Firestore scalable backend
- Cloud Run auto-scaling

---

## ☁️ Deployment

```bash
gcloud run deploy mindmap \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key,GEMINI_MODEL=models/gemini-pro
```

---

## 🎬 Demo Video

👉 https://youtu.be/rCC067HyslE

---

## 🏆 Why This Project Stands Out

- 🔥 AI + Cognitive Science combination
- 🧠 Real-world learning problem
- ⚡ Fully deployed system
- 🏗️ Clean architecture
- 📈 Scalable and production-ready

---

## 👩‍💻 Author

**Balbir Kaur**

---

## 🎯 Final Note

> MindMap doesn’t just help students study —
> it helps them **remember smarter**.

---
