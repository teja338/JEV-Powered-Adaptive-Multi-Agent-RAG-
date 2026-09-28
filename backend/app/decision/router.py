import json
import logging
from typing import Dict, Any, Tuple, List
from backend.app.decision.decision_engine import DecisionEngine
from backend.app.agents.rag_agent import rag_agent
from backend.app.agents.web_agent import web_agent
from backend.app.agents.code_agent import code_agent
from backend.app.models.schemas import ExecutionState, JEVDecision, SourceItem, ExecutionStep
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.agents = {
            "rag": rag_agent,
            "web": web_agent,
            "code": code_agent
        }

    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Executes complete JEV Adaptive Multi-Agent workflow:
        User Query -> Preserve Original Query -> Real JEV Decision -> Agent Execution -> Verification -> Pass/Fail -> JEV Re-decision -> Final Synthesis -> Original Query Validation
        """
        # 1. ALWAYS PRESERVE ORIGINAL USER QUERY
        original_query = query.strip()
        state = ExecutionState(
            original_query=original_query,
            current_query=original_query,
            rewritten_query=None,
            decision_source="jev"
        )
        re_decisions: List[JEVDecision] = []

        # 2. Step 1: Initial JEV Decision
        state.execution_trace.append({"step": "jev_initial_decision", "status": "running"})
        initial_decision = await self.decision_engine.decide_initial_route(original_query)
        state.decision_source = "fallback" if initial_decision.is_fallback else "jev"
        
        state.execution_trace.append({
            "step": "jev_initial_decision",
            "status": "completed",
            "details": {
                "selected_agent": initial_decision.agent,
                "confidence": initial_decision.confidence if not initial_decision.is_fallback else 0.0,
                "reasoning": initial_decision.reasoning,
                "is_fallback": initial_decision.is_fallback
            }
        })

        current_decision = initial_decision
        max_orchestration_steps = 3
        step_count = 0
        final_answer = ""
        final_verification = {}

        while step_count < max_orchestration_steps:
            step_count += 1
            agent_type = current_decision.agent
            state.current_agent = agent_type
            if agent_type not in state.previous_agents:
                state.previous_agents.append(agent_type)

            target_agent = self.agents.get(agent_type, rag_agent)
            
            # Execute selected agent
            agent_answer, verification, state = await target_agent.execute(state)

            if verification.get("sufficient", False):
                final_verification = verification
                state.execution_trace.append({"step": "verification_passed", "status": "passed"})

                # SPECIAL CASE FOR CODE AGENT: Code agent returns direct solution
                if agent_type == "code" and agent_answer:
                    final_answer = agent_answer
                else:
                    # FINAL SYNTHESIS: Generate grounded response using accumulated evidence
                    state.execution_trace.append({"step": "final_synthesis", "status": "running"})
                    final_answer = await self._synthesize_final_answer(original_query, state)
                    
                    # Original-query validation check before marking workflow complete
                    if not self._check_original_query_match(original_query, final_answer):
                        logger.warning("Final answer failed original query intent check. Regenerating strictly against original query...")
                        final_answer = await self._synthesize_final_answer(original_query, state)

                    state.execution_trace.append({"step": "final_synthesis", "status": "completed"})

                state.execution_trace.append({"step": "workflow_complete", "status": "completed"})
                break
            else:
                # Verification failed -> Send state to JEV for RE-DECISION
                state.execution_trace.append({
                    "step": "verification_failed",
                    "status": "warning",
                    "details": {
                        "agent": agent_type,
                        "reason": verification.get("reason", "Insufficient evidence"),
                        "missing_information": verification.get("missing_information", [])
                    }
                })

                if step_count >= max_orchestration_steps:
                    # Max orchestration attempts reached
                    final_verification = verification
                    final_answer = (
                        f"### ⚠️ Evidence Verification Incomplete\n\n"
                        f"**Original Query**: *\"{original_query}\"*\n\n"
                        f"**Status**: The multi-agent workflow was unable to collect verified evidence after {max_orchestration_steps} attempts.\n\n"
                        f"**Missing Information**: {', '.join(verification.get('missing_information', ['Incomplete context']))}\n\n"
                        f"**Analysis**: {verification.get('reason', 'Evidence was insufficient to generate a fully grounded answer.')}"
                    )
                    break

                # JEV RE-DECISION
                state.redecision_count += 1
                state.execution_trace.append({"step": "jev_re_decision", "status": "running"})
                re_decision = await self.decision_engine.decide_next_action(original_query, state)
                re_decisions.append(re_decision)

                state.execution_trace.append({
                    "step": "jev_re_decision",
                    "status": "completed",
                    "details": {
                        "next_agent": re_decision.agent,
                        "confidence": re_decision.confidence if not re_decision.is_fallback else 0.0,
                        "reasoning": re_decision.reasoning,
                        "is_fallback": re_decision.is_fallback
                    }
                })

                current_decision = re_decision

        # Format sources
        formatted_sources = []
        for c in state.retrieved_chunks:
            formatted_sources.append(SourceItem(
                id=c.get("id"),
                title=c.get("filename", "Document Chunk"),
                content=c.get("content", ""),
                source_type="document",
                url_or_file=c.get("filename", "Document"),
                score=c.get("score")
            ))

        for w in state.web_sources:
            formatted_sources.append(SourceItem(
                title=w.get("title", "Web Source"),
                content=w.get("content", ""),
                source_type="web",
                url_or_file=w.get("url_or_file", "#")
            ))

        # Build clean ExecutionSteps for UI
        execution_steps = []
        for item in state.execution_trace:
            execution_steps.append(ExecutionStep(
                step=item.get("step", ""),
                status=item.get("status", "completed"),
                details=item.get("details")
            ))

        state.final_answer = final_answer

        return {
            "answer": final_answer,
            "decision": initial_decision,
            "re_decisions": re_decisions,
            "execution": execution_steps,
            "verification": final_verification,
            "sources": formatted_sources,
            "state": state
        }

    async def _synthesize_final_answer(self, original_query: str, state: ExecutionState) -> str:
        """Synthesizes final answer directly answering original_query using accumulated RAG & Web evidence."""
        rag_evidence = "\n\n".join([f"Document Chunk [{c.get('filename','doc')}]:\n{c['content']}" for c in state.retrieved_chunks])
        web_evidence = "\n\n".join([f"Web Source [{w.get('title','web')}]:\n{w['content']}" for w in state.web_sources])

        prompt = (
            f"ORIGINAL USER QUESTION: '{original_query}'\n\n"
            f"RETRIEVED DOCUMENT EVIDENCE (RAG):\n{rag_evidence or 'None'}\n\n"
            f"RETRIEVED WEB EVIDENCE:\n{web_evidence or 'None'}\n\n"
            "INSTRUCTIONS:\n"
            "1. You must DIRECTLY answer the ORIGINAL USER QUESTION based ONLY on the evidence above.\n"
            "2. DO NOT change the topic or introduce unrelated concepts unless specifically asked for in the user question.\n"
            "3. Format your response cleanly using Markdown sections, bullet points, and exact facts.\n"
            "4. Include clear citations to document filenames or web source titles where appropriate."
        )
        return await llm_service.generate(prompt)

    def _check_original_query_match(self, original_query: str, answer: str) -> bool:
        """Original query intent validation check before answer delivery."""
        if not answer or len(answer.strip()) < 10:
            return False
        # Prevent semantic drift into unrelated topics
        if "ats scanning" in answer.lower() and "ats" not in original_query.lower():
            return False
        return True

orchestrator = MultiAgentOrchestrator()
