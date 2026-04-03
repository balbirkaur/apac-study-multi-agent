# MindMap – AI Study Productivity Assistant

## 🚀 Overview

MindMap is a **multi-agent AI productivity assistant** designed to help students learn smarter by tracking what they forget and guiding them on what to study next.

Unlike traditional task managers, MindMap uses the **forgetting curve** to prioritize learning, generate quizzes, and create personalized daily study plans.

---

## 🎯 Problem Statement

Students often:

- Forget what they study over time
- Don’t know what to revise next
- Use static task lists that ignore memory retention

---

## 💡 Solution

MindMap solves this by:

- Tracking **concept-level retention**
- Identifying **weak areas automatically**
- Generating **AI-powered quizzes**
- Creating **daily revision plans**

---

## 🧠 Key Features

### ✅ Multi-Agent System

- Ingestion Agent → Extracts concepts from notes
- Knowledge Graph Agent → Organizes concepts
- Diagnostic Agent → Generates quizzes
- Intervention Agent → Suggests what to study next
- Connection Agent → Builds concept relationships

---

### 📊 Retention Tracking

- Uses **forgetting curve logic**
- Calculates retention score (0–1)
- Prioritizes weakest concepts

---

### 📝 Smart Quiz Generation

- AI-generated MCQs using Gemini
- Targets weakest concepts first

---

### 📅 Daily Study Planner

- Suggests what to study today
- Focuses on high-urgency concepts

---

### 💾 Persistent Storage

- Firestore database
- Stores:
  - Concepts
  - Retention states
  - Learning progress

---

## 🏗️ Architecture

User → FastAPI → Orchestrator → Agents
                  ↓
              Firestore DB
                  ↓
              Gemini AI

---

## ⚙️ Tech Stack

- FastAPI (Backend API)
- Google Firestore (Database)
- Gemini AI (LLM)
- Python (Core logic)

---

## 📦 Installation

```bash
git clone https://github.com/balbirkaur/apac-study-multi-agent.git
cd apac-study-multi-agent
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

## 🔑 Environment Setup

Create `.env` file:

```env
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_project_id
```

Authenticate:

```bash
gcloud auth application-default login
```

---

## ▶️ Run the Project

```bash
uvicorn api.main:app --reload --port 8080
```

Open Swagger UI:

```
http://127.0.0.1:8080/docs
```

---

## 🧪 API Endpoints

### 📥 Ingest Study Content

```
POST /ingest/text
```

---

### 📊 Retention Dashboard

```
GET /retention/{student_id}
```

---

### 📚 Review Concepts

```
GET /review/{student_id}
```

---

### 🧠 Generate Quiz

```
GET /quiz/{student_id}/weakest
```

---

### 📅 Daily Plan

```
GET /daily/{student_id}
```

---

### 🤖 Chat Assistant

```
POST /chat
```

---

## 🎬 Demo Flow

1. Ingest study notes
2. View retention dashboard
3. Generate quiz for weakest concept
4. Get daily study plan

---

## 🏆 Why This Project Stands Out

- Combines **AI + learning science**
- Goes beyond task management → manages **memory**
- Fully automated study workflow
- Scalable multi-agent architecture

---

## 🔮 Future Enhancements

- Google Calendar integration
- Mobile app
- Real-time notifications
- Personalized learning analytics

---

## 👨‍💻 Author

Balbir Kaur

---

## ⭐ Tagline

“MindMap helps you remember what matters.”
