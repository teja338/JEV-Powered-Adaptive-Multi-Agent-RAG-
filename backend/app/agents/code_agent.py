import logging
from typing import Dict, Any, Tuple
from backend.app.agents.base_agent import BaseAgent
from backend.app.models.schemas import ExecutionState
from backend.app.verification.code_verifier import code_verifier
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class CodeAgent(BaseAgent):
    def __init__(self):
        pass

    async def execute(self, state: ExecutionState) -> Tuple[str, Dict[str, Any], ExecutionState]:
        original_query = state.original_query
        state.execution_trace.append({"step": "code_generation", "status": "running"})

        prompt = (
            f"User Coding Request: {original_query}\n\n"
            "Provide clean, well-commented Python code to solve this request. "
            "Structure your response with a Python code block followed by a brief complexity analysis."
        )
        response_text = await llm_service.generate(prompt)

        state.execution_trace.append({"step": "code_generation", "status": "completed"})

        # Code verification
        verification = await code_verifier.verify(original_query, response_text, response_text)
        state.verification = verification.dict()
        state.execution_trace.append({"step": "code_verification", "status": "passed" if verification.sufficient else "failed"})

        return response_text, verification.dict(), state

code_agent = CodeAgent()
