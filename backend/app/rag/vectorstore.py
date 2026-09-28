import os
import uuid
import logging
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from backend.app.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        self.collection = self.client.get_or_create_collection(name="jev_rag_collection")
        logger.info("Loading sentence transformer model all-MiniLM-L6-v2...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def add_documents(self, doc_id: str, filename: str, chunks: List[str]) -> int:
        if not chunks:
            return 0
        embeddings = self.model.encode(chunks).tolist()
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": doc_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.collection.count() == 0:
            return []
        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self.collection.count())
        )

        output = []
        if results and results.get("documents"):
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            ids = results["ids"][0]
            distances = results["distances"][0] if "distances" in results else [0.0]*len(docs)

            for d, m, i, dist in zip(docs, metas, ids, distances):
                # distance to similarity score
                score = round(1.0 / (1.0 + float(dist)), 4)
                output.append({
                    "id": i,
                    "content": d,
                    "filename": m.get("filename", "unknown"),
                    "doc_id": m.get("doc_id", ""),
                    "score": score
                })
        return output

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        if self.collection.count() == 0:
            return []
        res = self.collection.get()
        output = []
        for d, m, i in zip(res["documents"], res["metadatas"], res["ids"]):
            output.append({
                "id": i,
                "content": d,
                "filename": m.get("filename", "unknown"),
                "doc_id": m.get("doc_id", "")
            })
        return output

    def delete_document(self, doc_id: str):
        res = self.collection.get(where={"doc_id": doc_id})
        if res and res.get("ids"):
            self.collection.delete(ids=res["ids"])

vector_store = VectorStore()
