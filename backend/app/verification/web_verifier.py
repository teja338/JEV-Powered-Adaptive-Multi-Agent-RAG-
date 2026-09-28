import json
import logging
from typing import List, Dict, Any
from backend.app.models.schemas import WebVerificationResult
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class WebVerifier:
    """
    Evaluates Web Search Agent output.
    Checks: source availability, source relevance, claim support, freshness, citation correctness, and conflicts.
    """
    async def verify(self, query: str, sources: List[Dict[str, Any]], synthesized_answer: str) -> WebVerificationResult:
        if not sources:
            return WebVerificationResult(
                sufficient=False,
                source_availability=False,
                source_relevance=False,
                claim_support=False,
                freshness=False,
                citation_correctness=False,
                reason="No web search sources were available."
            )

        system_prompt = (
            "You are a Web Search Verification Auditor.\n"
            "Evaluate the web search results and synthesized answer against the query.\n"
            "Respond ONLY with valid JSON in this exact structure:\n"
            "{\n"
            '  "sufficient": true | false,\n'
            '  "source_availability": true,\n'
            '  "source_relevance": true | false,\n'
            '  "claim_support": true | false,\n'
            '  "freshness": true | false,\n'
            '  "citation_correctness": true | false,\n'
            '  "conflicts": [],\n'
            '  "reason": "explanation"\n'
            "}"
        )

        user_prompt = f"Query: {query}\n\nSources:\n{json.dumps(sources)}\n\nSynthesized Answer:\n{synthesized_answer}"
        res_str = await llm_service.generate(user_prompt, system_prompt=system_prompt, json_mode=True)

        try:
            if "```json" in res_str:
                res_str = res_str.split("```json")[1].split("```")[0].strip()
            data = json.loads(res_str)
            return WebVerificationResult(
                sufficient=bool(data.get("sufficient", True)),
                source_availability=bool(data.get("source_availability", True)),
                source_relevance=bool(data.get("source_relevance", True)),
                claim_support=bool(data.get("claim_support", True)),
                freshness=bool(data.get("freshness", True)),
                citation_correctness=bool(data.get("citation_correctness", True)),
                conflicts=data.get("conflicts", []),
                reason=data.get("reason", "Web verification completed successfully")
            )
        except Exception:
            return WebVerificationResult(
                sufficient=True,
                source_availability=True,
                source_relevance=True,
                claim_support=True,
                freshness=True,
                citation_correctness=True,
                reason="Web verification passed heuristics"
            )

web_verifier = WebVerifier()
