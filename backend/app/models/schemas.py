from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class JEVDecision(BaseModel):
    agent: str = Field(description="Selected agent: 'rag', 'web', or 'code'")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: Optional[str] = Field(default="", description="Reasoning behind the decision")
    is_fallback: bool = Field(default=False, description="True if a fallback decision engine was used")

class ExecutionStep(BaseModel):
    step: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'warning', 'passed'
    details: Optional[Dict[str, Any]] = None

class RAGVerificationResult(BaseModel):
    sufficient: bool
    relevant: bool
    coverage: float
    grounded: bool
    confidence: float
    evidence_quality: float = 0.8
    missing_information: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    reason: Optional[str] = ""

class WebVerificationResult(BaseModel):
    sufficient: bool
    source_availability: bool
    source_relevance: bool
    claim_support: bool
    freshness: bool
    citation_correctness: bool
    conflicts: List[str] = Field(default_factory=list)
    reason: Optional[str] = ""

class CodeVerificationResult(BaseModel):
    sufficient: bool
    syntax: bool
    requirements: bool
    explanation_consistency: bool
    tests: bool = True
    complexity_claims: Optional[str] = None
    reason: Optional[str] = ""

class SourceItem(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    content: str
    source_type: str  # 'document' or 'web'
    url_or_file: str
    score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExecutionState(BaseModel):
    original_query: str
    current_query: str
    rewritten_query: Optional[str] = None

    current_agent: Optional[str] = None
    previous_agents: List[str] = Field(default_factory=list)

    retrieval_attempt: int = 0
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list)
    web_sources: List[Dict[str, Any]] = Field(default_factory=list)
    tool_results: List[Dict[str, Any]] = Field(default_factory=list)

    verification: Optional[Dict[str, Any]] = None

    retry_count: int = 0
    redecision_count: int = 0

    decision_source: str = "jev"
    decision_history: List[Dict[str, Any]] = Field(default_factory=list)

    execution_trace: List[Dict[str, Any]] = Field(default_factory=list)
    final_answer: Optional[str] = None

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    decision: JEVDecision
    re_decisions: List[JEVDecision] = Field(default_factory=list)
    execution: List[ExecutionStep]
    verification: Dict[str, Any]
    sources: List[SourceItem] = Field(default_factory=list)
    state: ExecutionState

class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunk_count: int
    status: str  # 'indexed', 'processing', 'error'
    uploaded_at: str
    file_size: int
