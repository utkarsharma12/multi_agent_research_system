# 🤖 Multi-Agent Research System

A powerful AI-driven research assistant that uses **5 specialized agents** orchestrated by **LangGraph** to plan, research, fact-check, summarize, and generate professional reports — powered by **Google Gemini**.

---

## 🏗️ Architecture

```
User
 │
 ▼
Frontend (Next.js 14 + TailwindCSS + shadcn/ui)
 │  REST API
 ▼
Backend API (FastAPI)
 │
 ▼
LangGraph Orchestrator
 ├── 🧠 Planner Agent     — Breaks query into research steps
 ├── 🔍 Research Agent    — Web + PDF + arXiv search
 ├── ✅ Fact Checker Agent — Validates sources & flags contradictions
 ├── 📝 Summarizer Agent  — Bullet points & key concepts
 └── 📊 Report Agent      — Full structured markdown report
 │
 ▼
RAG Pipeline (LangChain + sentence-transformers)
 │
 ▼
ChromaDB (vector store) + SQLite (relational DB)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Google Gemini API key ([get one here](https://aistudio.google.com/))

### 1. Clone & configure
```bash
# Copy environment file
cp .env.example backend/.env
# Edit backend/.env and add your GOOGLE_API_KEY
```

### 2. Start the backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Open the app
Visit **http://localhost:3000** 🎉

---

## 🤖 Agents

| Agent | Responsibility |
|-------|---------------|
| **Planner** | Decomposes your query into 3–5 research steps |
| **Researcher** | Searches the web, arXiv papers, and uploaded PDFs |
| **Fact Checker** | Cross-references sources, flags hallucinations |
| **Summarizer** | Extracts key concepts and bullet-point notes |
| **Reporter** | Generates a full report with references |

---

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Run a research query through all agents |
| GET | `/api/chat/history` | Get past chat sessions |
| POST | `/api/documents/upload` | Upload a PDF for RAG indexing |
| GET | `/api/documents` | List indexed documents |
| GET | `/api/reports` | List generated reports |
| GET | `/api/reports/{id}` | Get a specific report |

API docs available at: **http://localhost:8000/docs**

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TailwindCSS, shadcn/ui, Zustand |
| Backend | FastAPI, Python 3.11+ |
| Agent Orchestration | LangGraph |
| LLM | Google Gemini 1.5 Pro |
| RAG | LangChain + sentence-transformers |
| Vector DB | ChromaDB |
| Relational DB | SQLite (dev) |
| Web Search | DuckDuckGo Search |
| Academic Search | arXiv API |
| PDF Processing | PyPDF |

---

## 📁 Project Structure

```
multi-agent-research-assistant/
├── frontend/               # Next.js frontend
│   ├── app/               # App Router pages
│   ├── components/        # UI components
│   │   ├── Chat/         # Chat interface
│   │   ├── Sidebar/      # Navigation
│   │   ├── Reports/      # Report viewer
│   │   └── Upload/       # PDF uploader
│   ├── store/            # Zustand state
│   └── services/         # API client
│
├── backend/               # FastAPI backend
│   ├── agents/           # LangGraph agents
│   ├── graph/            # LangGraph workflow
│   ├── rag/              # RAG pipeline
│   ├── api/routes/       # API endpoints
│   ├── database/         # DB models & schemas
│   ├── services/         # External services
│   └── main.py          # App entry point
│
└── README.md
```
