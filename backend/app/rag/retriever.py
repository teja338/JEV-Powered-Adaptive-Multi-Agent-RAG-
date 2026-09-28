import logging
from typing import List, Dict, Any
from backend.app.rag.vectorstore import vector_store
from backend.app.rag.bm25 import bm25_retriever

logger = logging.getLogger(__name__)

class HybridRetriever:
    def __init__(self):
        pass

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        dense_results = vector_store.search(query, top_k=top_k*2)
        bm25_results = bm25_retriever.search(query, top_k=top_k*2)

        # Merge results with Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, Dict[str, Any]] = {}
        k_constant = 60

        for rank, item in enumerate(dense_results):
            cid = item["id"]
            if cid not in rrf_scores:
                rrf_scores[cid] = {"item": item, "score": 0.0}
            rrf_scores[cid]["score"] += 1.0 / (k_constant + rank + 1)

        for rank, item in enumerate(bm25_results):
            cid = item["id"]
            if cid not in rrf_scores:
                rrf_scores[cid] = {"item": item, "score": 0.0}
            rrf_scores[cid]["score"] += 1.0 / (k_constant + rank + 1)

        sorted_items = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
        
        merged = []
        for entry in sorted_items[:top_k]:
            it = entry["item"]
            it["rrf_score"] = round(entry["score"], 5)
            merged.append(it)

        return merged

    def rerank_and_compress(self, query: str, chunks: List[Dict[str, Any]], max_len: int = 2000) -> List[Dict[str, Any]]:
        """Simple heuristic reranking and context compression based on query token matches."""
        query_words = set(query.lower().split())
        for chunk in chunks:
            c_words = set(chunk["content"].lower().split())
            overlap = len(query_words.intersection(c_words))
            chunk["rerank_score"] = round(chunk.get("rrf_score", 0.0) + (overlap * 0.1), 4)

        reranked = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
        
        # Compress text length
        compressed = []
        total_len = 0
        for chunk in reranked:
            if total_len + len(chunk["content"]) <= max_len:
                compressed.append(chunk)
                total_len += len(chunk["content"])
            else:
                break
        return compressed

hybrid_retriever = HybridRetriever()
