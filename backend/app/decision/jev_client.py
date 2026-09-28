import os
import json
import logging
import httpx
from typing import Dict, Any, Optional

from backend.app.config import settings
from backend.app.models.schemas import JEVDecision, ExecutionState

logger = logging.getLogger(__name__)


class JEVClient:
    def __init__(self, api_key: str = None, model: str = None):

        self.api_key = (
            api_key
            or settings.TYPESAFE_API_KEY
        )

        self.model = (
            model
            or settings.JEV_MODEL
            or "jev-1.13.0"
        )

        self.system_one_url = (
            "https://api.typesafe.ai/v1/systemone"
        )

    async def get_decision(
        self,
        query: str,
        state: Optional[ExecutionState] = None
    ) -> JEVDecision:

        original_query = (
            state.original_query
            if state
            else query
        )

        if (
            not self.api_key
            or len(self.api_key.strip()) < 5
        ):
            logger.warning(
                "No valid TYPESAFE_API_KEY found. "
                "Using Fallback Router."
            )

            return self._fallback_routing(
                original_query,
                state,
                reason="Missing TypeSafe API Key"
            )

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }

        available_agents = {
            "rag": (
                "Uploaded documents, private knowledge base, "
                "PDFs, resumes, and document-grounded questions."
            ),
            "web": (
                "Current information, latest news, recent events, "
                "external research, or information that may have changed."
            ),
            "code": (
                "Programming, debugging, code generation, algorithms, "
                "software development, and technical implementation."
            )
        }

        context_state: Dict[str, Any] = {
            "original_query": original_query,
            "available_agents": available_agents,
            "current_agent": (
                state.current_agent
                if state
                else None
            ),
            "previous_agents": (
                state.previous_agents
                if state
                else []
            ),
            "retrieval_attempt": (
                state.retrieval_attempt
                if state
                else 0
            ),
            "verification_status": (
                state.verification
                if state
                else None
            )
        }

        questions = {
            "route": {
                "type": "choice",
                "instructions": (
                    "Select exactly one specialized agent for the "
                    "ORIGINAL USER QUESTION. Use RAG for uploaded/private "
                    "knowledge, WEB for current/external information, "
                    "and CODE for programming or debugging. Consider "
                    "the current execution state and verification status."
                ),
                "criteria": available_agents
            }
        }

        payload = {
            "model": self.model,
            "state": context_state,
            "questions": questions
        }

        try:
            async with httpx.AsyncClient(
                timeout=15.0
            ) as client:

                response = await client.post(
                    self.system_one_url,
                    headers=headers,
                    json=payload
                )

            if response.status_code == 200:

                data = response.json()

                logger.info(
                    "JEV response received from TypeSafe."
                )

                answers = data.get("answers", {})

                route_answer = answers.get(
                    "route",
                    {}
                )

                agent = route_answer.get("choice")

                try:
                    confidence = float(
                        route_answer.get(
                            "confidence",
                            0.0
                        )
                    )
                except (TypeError, ValueError):
                    confidence = 0.0

                probabilities = route_answer.get(
                    "probabilities",
                    {}
                )

                if agent in available_agents:

                    reasoning = self._build_reasoning(
                        agent,
                        confidence,
                        probabilities,
                        state
                    )

                    return JEVDecision(
                        agent=agent,
                        confidence=confidence,
                        reasoning=reasoning,
                        is_fallback=False
                    )

                logger.warning(
                    f"Invalid JEV route returned: {agent}"
                )

            else:

                logger.error(
                    f"TypeSafe JEV API error "
                    f"{response.status_code}: {response.text}"
                )

        except Exception as e:

            logger.exception(
                f"TypeSafe JEV request failed: {e}"
            )

        return self._fallback_routing(
            original_query,
            state,
            reason="TypeSafe JEV API unavailable"
        )

    def _build_reasoning(
        self,
        agent: str,
        confidence: float,
        probabilities: Dict[str, Any],
        state: Optional[ExecutionState]
    ) -> str:

        probability_text = ""

        if isinstance(probabilities, dict) and probabilities:

            parts = []

            for name, value in probabilities.items():
                try:
                    parts.append(
                        f"{name}={float(value):.2f}"
                    )
                except (TypeError, ValueError):
                    parts.append(
                        f"{name}={value}"
                    )

            probability_text = (
                " Distribution: "
                + ", ".join(parts)
                + "."
            )

        if (
            state
            and state.current_agent == "rag"
            and state.verification
            and not state.verification.get(
                "sufficient",
                True
            )
            and agent == "web"
        ):
            return (
                "JEV selected the Web Agent because the previous "
                "RAG result was insufficient. "
                f"Confidence={confidence:.2f}."
                f"{probability_text}"
            )

        return (
            f"JEV selected the {agent.upper()} Agent. "
            f"Confidence={confidence:.2f}."
            f"{probability_text}"
        )

    def _fallback_routing(
        self,
        query: str,
        state: Optional[ExecutionState],
        reason: str
    ) -> JEVDecision:

        logger.info(
            f"Using Fallback Router. Reason: {reason}"
        )

        if (
            state
            and state.current_agent == "rag"
            and state.verification
            and not state.verification.get(
                "sufficient",
                True
            )
        ):
            return JEVDecision(
                agent="web",
                confidence=0.0,
                reasoning=(
                    "Fallback Router: RAG evidence was insufficient, "
                    f"routing to Web Agent ({reason})"
                ),
                is_fallback=True
            )

        q = query.lower()

        code_keywords = [
            "python",
            "code",
            "script",
            "function",
            "algorithm",
            "debug",
            "debugging",
            "binary search",
            "program",
            "programming",
            "class ",
            "def ",
            "exception",
            "error",
            "syntax",
            "compile",
            "javascript",
            "java",
            "c++",
            "sql"
        ]

        web_keywords = [
            "latest",
            "news",
            "current",
            "today",
            "recent",
            "yesterday",
            "tomorrow",
            "weather",
            "who is",
            "what happened",
            "live",
            "price",
            "stock",
            "market"
        ]

        if any(k in q for k in code_keywords):
            agent = "code"

        elif any(k in q for k in web_keywords):
            agent = "web"

        else:
            agent = "rag"

        return JEVDecision(
            agent=agent,
            confidence=0.0,
            reasoning=(
                "Fallback Router based on semantic heuristics "
                f"({reason})"
            ),
            is_fallback=True
        )
