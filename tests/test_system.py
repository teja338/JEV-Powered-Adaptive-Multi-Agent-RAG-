import pytest
import asyncio
from backend.app.decision.jev_client import JEVClient
from backend.app.decision.router import orchestrator
from backend.app.rag.vectorstore import vector_store
from backend.app.rag.bm25 import bm25_retriever
from backend.app.verification.rag_verifier import rag_verifier

@pytest.mark.asyncio
async def test_jev_initial_routing():
    client = JEVClient()
    dec = await client.get_decision("Write Python code for binary search.")
    assert dec.agent in ["rag", "web", "code"]

@pytest.mark.asyncio
async def test_code_query():
    res = await orchestrator.process_query("Write a Python script to calculate Fibonacci sequence.")
    assert res["decision"].agent in ["rag", "web", "code"]
    assert len(res["execution"]) > 0

@pytest.mark.asyncio
async def test_insufficient_rag_context():
    # Searching for unknown topic in empty vectorstore
    result = await rag_verifier.verify("What is the secret code of Project X?", [])
    assert result.sufficient == False
    assert result.coverage == 0.0

@pytest.mark.asyncio
async def test_orchestrator_complete_flow():
    res = await orchestrator.process_query("What is the completion percentage of foundation work?")
    assert "answer" in res
    assert "decision" in res
    assert "execution" in res
