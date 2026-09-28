import logging
from typing import Dict, Any, Tuple
from backend.app.agents.base_agent import BaseAgent
from backend.app.models.schemas import ExecutionState
from backend.app.rag.adaptive import adaptive_rag
from backend.app.verification.rag_verifier import rag_verifier
from backend.app.services.llm_service import llm_service
from backend.app.config import settings

logger = logging.getLogger(__name__)

class RAGAgent(BaseAgent):
    def __init__(self):
        pass

    async def execute(self, state: ExecutionState) -> Tuple[str, Dict[str, Any], ExecutionState]:
        original_query = state.original_query
        max_retries = settings.MAX_RAG_RETRIES
        current_attempt = 1
        missing_info = None

        state.execution_trace.append({"step": "rag_agent_start", "status": "completed"})

        chunks = []
        verifier_result = None

        while current_attempt <= max_retries:
            state.retrieval_attempt = current_attempt
            state.execution_trace.append({"step": f"adaptive_rag_attempt_{current_attempt}", "status": "running"})

            # Adaptive RAG steps: Query Rewrite (Search query only!) -> Hybrid Retrieval -> Rerank & Compress
            retrieval_res = await adaptive_rag.execute_retrieval(original_query, attempt=current_attempt, missing_info=missing_info)
            chunks = retrieval_res["chunks"]

            state.retrieved_chunks = chunks
            state.execution_trace.append({
                "step": f"adaptive_rag_retrieval_{current_attempt}",
                "status": "completed",
                "details": {
                    "search_query": retrieval_res["rewritten_query"],
                    "chunks_retrieved": len(chunks)
                }
            })

            # Verification step against original_query
            verifier_result = await rag_verifier.verify(original_query, chunks)
            state.verification = verifier_result.dict()

            if verifier_result.sufficient:
                state.execution_trace.append({"step": f"rag_verification_attempt_{current_attempt}", "status": "passed"})
                logger.info(f"RAG evidence sufficient on attempt {current_attempt}")
                break
            else:
                state.execution_trace.append({
                    "step": f"rag_verification_attempt_{current_attempt}",
                    "status": "failed",
                    "details": {
                        "reason": verifier_result.reason,
                        "missing_information": verifier_result.missing_information
                    }
                })
                logger.warning(f"RAG evidence insufficient on attempt {current_attempt}")
                missing_info = verifier_result.missing_information
                current_attempt += 1

        if verifier_result and verifier_result.sufficient:
            # Context evidence collected -> final synthesis happens in orchestrator
            return "", verifier_result.dict(), state
        else:
            # Insufficient evidence after max retries
            state.retry_count = current_attempt - 1
            return "", verifier_result.dict() if verifier_result else {}, state

rag_agent = RAGAgent()
