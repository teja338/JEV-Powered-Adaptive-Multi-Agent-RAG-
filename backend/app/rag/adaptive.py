import json
import logging
from typing import List, Dict, Any
from backend.app.services.llm_service import llm_service
from backend.app.rag.retriever import hybrid_retriever

logger = logging.getLogger(__name__)

class AdaptiveRAGPipeline:
    def __init__(self):
        pass

    async def rewrite_query(self, original_query: str, attempt: int, missing_info: List[str] = None) -> str:
        """
        Rewrites original query to generate ONLY a better search/retrieval query.
        NEVER generates an answer or summary text.
        Validates intent preservation against original_query.
        """
        if attempt == 1 and not missing_info:
            return original_query

        prompt = (
            f"Original user question: '{original_query}'\n"
            f"Attempt: {attempt}\n"
            f"Missing information needed: {missing_info or 'None'}\n\n"
            "Task: Generate a concise, keyword-rich search query suitable for retrieving exact factual document chunks.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Output ONLY the search query string.\n"
            "2. Do NOT answer the question.\n"
            "3. Do NOT generate Markdown headers, explanations, or summaries.\n"
            "4. Preserve the exact user intent of the original question."
        )
        rewritten = await llm_service.generate(prompt)
        clean_query = rewritten.strip('"').strip().split("\n")[0]

        # Validation check: Ensure rewrite preserves intent and is not an LLM answer
        if clean_query.startswith("#") or "###" in clean_query or len(clean_query.split()) > 30:
            logger.warning(f"Query rewrite produced invalid answer text ('{clean_query[:50]}...'). Reverting to original query.")
            return original_query

        return clean_query

    async def execute_retrieval(self, original_query: str, attempt: int = 1, missing_info: List[str] = None) -> Dict[str, Any]:
        """Runs adaptive retrieval pipeline: rewrite -> hybrid retrieval -> rerank & compress."""
        rewritten_query = await self.rewrite_query(original_query, attempt, missing_info)
        raw_chunks = hybrid_retriever.retrieve(rewritten_query, top_k=6)
        compressed_chunks = hybrid_retriever.rerank_and_compress(rewritten_query, raw_chunks)

        return {
            "attempt": attempt,
            "original_query": original_query,
            "rewritten_query": rewritten_query,
            "chunks": compressed_chunks
        }

adaptive_rag = AdaptiveRAGPipeline()
