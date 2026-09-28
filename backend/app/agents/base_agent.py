from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from backend.app.models.schemas import ExecutionState

class BaseAgent(ABC):
    @abstractmethod
    async def execute(self, state: ExecutionState) -> Tuple[str, Dict[str, Any], ExecutionState]:
        """
        Executes the agent's core task.
        Returns (generated_answer, verification_result_dict, updated_execution_state).
        """
        pass
