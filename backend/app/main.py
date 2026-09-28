import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.chat import router as chat_router
from backend.app.api.documents import router as doc_router

app = FastAPI(
    title="JEV-Powered Adaptive Multi-Agent RAG System",
    description="Decision-First AI Agent Router using OpenRouter JEV, Adaptive RAG, Web & Code Agents, and Structured Verification.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(doc_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
