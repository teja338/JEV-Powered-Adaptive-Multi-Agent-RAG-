from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import ChatRequest, ChatResponse
from backend.app.decision.router import orchestrator

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        result = await orchestrator.process_query(request.query.strip())
        return ChatResponse(
            answer=result["answer"],
            decision=result["decision"],
            re_decisions=result["re_decisions"],
            execution=result["execution"],
            verification=result["verification"],
            sources=result["sources"],
            state=result["state"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration error: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "JEV Adaptive Multi-Agent Router"}
