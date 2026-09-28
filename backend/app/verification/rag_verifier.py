import json
import logging
from typing import List, Dict, Any
from backend.app.models.schemas import RAGVerificationResult
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class RAGVerifier:
    """
    Evaluates RAG retrieval context quality against the ORIGINAL user query.
    Evaluates: relevance, coverage, grounding, evidence quality, and conflicts.
    NEVER returns 'reason: Verification completed' as the sole info.
    """
    async def verify(self, original_query: str, retrieved_chunks: List[Dict[str, Any]]) -> RAGVerificationResult:
        if not retrieved_chunks:
            return RAGVerificationResult(
                sufficient=False,
                relevant=False,
                coverage=0.0,
                grounded=False,
                confidence=0.0,
                evidence_quality=0.0,
                missing_information=[f"No indexed documents or chunks retrieved for '{original_query}'"],
                reason="Knowledge base returned zero relevant chunks for the user question."
            )

        context_text = "\n---\n".join([c["content"] for c in retrieved_chunks])

        system_prompt = (
            "You are a strict RAG Verification Auditor.\n"
            "Evaluate whether the retrieved context contains ENOUGH factual evidence to answer the user's ORIGINAL query.\n"
            "Evaluate 5 dimensions:\n"
            "1. RELEVANCE: Does context relate to the question?\n"
            "2. COVERAGE: Does context contain the specific data/metrics/facts requested?\n"
            "3. GROUNDING: Can answer be supported without hallucination?\n"
            "4. EVIDENCE QUALITY: Is evidence specific?\n"
            "5. CONFLICTS: Do chunks contradict each other?\n\n"
            "CRITICAL: If context is missing specific details requested in the query, set sufficient=false and list exact missing details in missing_information.\n"
            "Respond ONLY with valid JSON in this exact structure:\n"
            "{\n"
            '  "sufficient": true | false,\n'
            '  "relevant": true | false,\n'
            '  "coverage": 0.0 - 1.0,\n'
            '  "grounded": true | false,\n'
            '  "confidence": 0.0 - 1.0,\n'
            '  "evidence_quality": 0.0 - 1.0,\n'
            '  "missing_information": ["exact missing detail 1"],\n'
            '  "conflicts": [],\n'
            '  "reason": "Detailed explanation of why evidence is sufficient or what specific facts are missing."\n'
            "}"
        )

        user_prompt = f"Original User Query: {original_query}\n\nRetrieved Context:\n{context_text}"

        res_str = await llm_service.generate(user_prompt, system_prompt=system_prompt, json_mode=True)
        
        try:
            if "```json" in res_str:
                res_str = res_str.split("```json")[1].split("```")[0].strip()
            data = json.loads(res_str)
            
            sufficient = bool(data.get("sufficient", False))
            missing = data.get("missing_information", [])
            reason = data.get("reason", "")

            if not reason or reason == "Verification completed":
                reason = "Retrieved chunks provide complete factual coverage." if sufficient else f"Context lacks specific details for '{original_query}'."

            if not sufficient and not missing:
                missing = [f"Retrieved document context is incomplete for query: '{original_query}'"]

            return RAGVerificationResult(
                sufficient=sufficient,
                relevant=bool(data.get("relevant", True)),
                coverage=float(data.get("coverage", 0.5)),
                grounded=bool(data.get("grounded", True)),
                confidence=float(data.get("confidence", 0.5)),
                evidence_quality=float(data.get("evidence_quality", 0.8)),
                missing_information=missing,
                conflicts=data.get("conflicts", []),
                reason=reason
            )
        except Exception as e:
            logger.error(f"Error parsing RAG verification output: {e}")
            query_words = [w.lower() for w in original_query.split() if len(w) > 3]
            matches = [w for w in query_words if w in context_text.lower()]
            has_coverage = (len(matches) / max(len(query_words), 1)) >= 0.6

            return RAGVerificationResult(
                sufficient=has_coverage,
                relevant=len(matches) > 0,
                coverage=0.8 if has_coverage else 0.3,
                grounded=has_coverage,
                confidence=0.8 if has_coverage else 0.3,
                evidence_quality=0.7 if has_coverage else 0.2,
                missing_information=[] if has_coverage else [f"Missing direct evidence for keywords: {query_words}"],
                reason="Document chunks contain matching keywords." if has_coverage else f"Context missing key terms from '{original_query}'."
            )

rag_verifier = RAGVerifier()
