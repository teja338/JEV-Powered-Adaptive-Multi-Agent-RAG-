from typing import Optional
from backend.app.decision.jev_client import JEVClient
from backend.app.models.schemas import JEVDecision, ExecutionState

class DecisionEngine:
    def __init__(self):
        self.client = JEVClient()

    async def decide_initial_route(self, query: str) -> JEVDecision:
        """Initial routing decision by JEV."""
        return await self.client.get_decision(query=query)

    async def decide_next_action(self, query: str, state: ExecutionState) -> JEVDecision:
        """Re-decision by JEV based on current execution state."""
        return await self.client.get_decision(query=query, state=state)
