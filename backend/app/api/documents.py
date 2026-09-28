import os
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from backend.app.rag.parser import DocumentParser, TextChunker
from backend.app.rag.vectorstore import vector_store
from backend.app.models.schemas import DocumentInfo
from backend.app.config import settings

router = APIRouter(prefix="/api/documents", tags=["documents"])

# In-memory document status metadata database
DOCUMENTS_DB: Dict[str, DocumentInfo] = {}

@router.post("/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
    doc_id = str(uuid.uuid4())
    file_path = os.path.join(settings.DOCUMENTS_DIR, f"{doc_id}_{file.filename}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse and index
    text = DocumentParser.parse_pdf(file_path)
    chunks = TextChunker.chunk_text(text)
    chunk_count = vector_store.add_documents(doc_id, file.filename, chunks)

    doc_info = DocumentInfo(
        id=doc_id,
        filename=file.filename,
        chunk_count=chunk_count,
        status="indexed",
        uploaded_at="Just now",
        file_size=len(content)
    )
    DOCUMENTS_DB[doc_id] = doc_info
    return doc_info

@router.get("", response_model=List[DocumentInfo])
async def list_documents():
    return list(DOCUMENTS_DB.values())

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    if doc_id in DOCUMENTS_DB:
        vector_store.delete_document(doc_id)
        del DOCUMENTS_DB[doc_id]
        return {"status": "success", "message": f"Document {doc_id} deleted successfully."}
    raise HTTPException(status_code=404, detail="Document not found")
