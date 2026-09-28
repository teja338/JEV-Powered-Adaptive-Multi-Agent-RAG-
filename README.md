# JEV-Powered Adaptive Multi-Agent RAG — Decision-First AI Agent Router

## Architecture Overview
The system implements a Decision-First AI Agent Router where **JEV** acts as the outer decision layer, delegating execution to three primary specialized agents: **RAG Agent**, **Web Agent**, and **Code Agent**.

```
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │     JEV     │
                    │ DECISION    │
                    │    LAYER    │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        ┌─────────┐   ┌─────────┐   ┌─────────┐
        │   RAG   │   │   WEB   │   │  CODE   │
        │  AGENT  │   │  AGENT  │   │  AGENT  │
        └────┬────┘   └────┬────┘   └────┬────┘
             │             │             │
             ▼             ▼             ▼
      ┌────────────┐    Search       Code Tools
      │ Adaptive   │
      │    RAG     │
      └─────┬──────┘
            │
     ┌──────┼──────────────┐
     ▼      ▼              ▼
  Rewrite  Hybrid        Rerank
           Retrieval
     │      │              │
     └──────┼──────────────┘
            ▼
       Evidence
            │
            ▼
       VERIFICATION
            │
       ┌────┴────┐
       │         │
      PASS      FAIL
       │         │
       ▼         ▼
    ANSWER      JEV
                 │
                 ▼
        ┌──────────────────┐
        │  NEXT DECISION   │
        └────────┬─────────┘
                 │
          ┌──────┼──────┐
          ▼      ▼      ▼
       Retry    Web    Code
        RAG
          │
          ▼
      Verification
          │
          ▼
        ANSWER
```

## Four Core Responsibilities
1. **JEV Layer**: Answers *"What should the system DO NEXT?"*
2. **RAG Agent**: Answers *"What information can I retrieve from the knowledge base?"*
3. **Adaptive RAG**: Answers *"How can I retrieve BETTER evidence?"* (via query rewriting, dense search + BM25 hybrid retrieval, RRF reranking, and context compression).
4. **Verification Layer**: Answers *"Is the current result GOOD ENOUGH and properly supported?"* (checks relevance, coverage, grounding, confidence, missing information).

## Tech Stack
- **Backend**: Python 3.10+, FastAPI, OpenRouter JEV Decisions API (`typesafe/jev-1.13`), ChromaDB, SentenceTransformers (`all-MiniLM-L6-v2`), BM25 (`rank_bm25`), PyMuPDF / pypdf.
- **Frontend**: React (JavaScript only), Vite, Tailwind CSS.

## Installation & Setup

### 1. Environment Configuration
Copy `.env.example` to `.env` and set your OpenRouter API Key:
```bash
OPENROUTER_API_KEY=your_openrouter_key
JEV_MODEL=typesafe/jev-1.13
MAX_RAG_RETRIES=2
```

### 2. Backend Setup
```bash
cd /home/user/jev-agent-router
PYTHONPATH=. /home/user/jev-agent-router/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd /home/user/jev-agent-router/frontend
npm run dev
```

### 4. Running Tests
```bash
PYTHONPATH=. /home/user/jev-agent-router/venv/bin/pytest tests/test_system.py
```
