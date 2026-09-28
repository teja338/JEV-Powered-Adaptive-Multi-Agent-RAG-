import logging
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from backend.app.rag.vectorstore import vector_store

logger = logging.getLogger(__name__)

class BM25Retriever:
    def __init__(self):
        pass

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        all_chunks = vector_store.get_all_chunks()
        if not all_chunks:
            return []

        corpus = [chunk["content"].lower().split() for chunk in all_chunks]
        bm25 = BM25Okapi(corpus)

        tokenized_query = query.lower().split()
        scores = bm25.get_scores(tokenized_query)

        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in indexed_scores[:top_k]:
            if score > 0:
                item = dict(all_chunks[idx])
                item["score"] = round(float(score), 4)
                results.append(item)

        return results

bm25_retriever = BM25Retriever()
