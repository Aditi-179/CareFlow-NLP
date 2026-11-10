from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.config import settings
from app.preprocessing import preprocess_query
from app.classification import classify_query, CATEGORIES
from app.retrieval import get_vector_store
from app.llm import get_rag_engine

router = APIRouter(prefix="/api", tags=["Healthcare Chatbot & NLP"])

class ChatHistoryMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000, description="User healthcare query")
    history: Optional[List[ChatHistoryMessage]] = Field(default=[], description="Active conversation session history")

class SourceReference(BaseModel):
    chunk_id: int
    document: str
    section: str
    text: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    category: str
    category_confidence: float
    matched_keywords: List[str]
    cleaned_query: str
    has_negation: bool
    negations_found: List[str]
    sources: List[SourceReference]
    total_sources: int
    disclaimer: str
    model_used: Optional[str] = None
    is_fallback: bool = False

@router.post("/chat", response_model=ChatResponse)
async def process_healthcare_query(payload: ChatRequest):
    """
    Core RAG Endpoint:
    1. Text Preprocessing (Tokenization, Negation Preservation, Noise Reduction)
    2. Query Intent Classification
    3. Dense Vector Semantic Search via FAISS
    4. Grounded Response Generation with Groq LLM
    """
    raw_query = payload.query.strip()
    if not raw_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. Preprocessing
    preprocessed = preprocess_query(raw_query)
    cleaned_query = preprocessed["normalized_query"]

    # 2. Healthcare Query Classification
    classification = classify_query(
        query=raw_query,
        informative_tokens=preprocessed["informative_tokens"]
    )
    category = classification["category"]

    # 3. FAISS Vector Search & Retrieval
    vector_store = get_vector_store()
    retrieved_chunks = vector_store.search(
        query=raw_query,
        top_k=settings.TOP_K_RETRIEVAL,
        threshold=settings.SIMILARITY_THRESHOLD
    )

    # 4. LLM Generation via Groq
    rag_engine = get_rag_engine()
    history_dicts = [h.model_dump() for h in payload.history] if payload.history else []
    
    llm_result = rag_engine.generate_response(
        query=raw_query,
        retrieved_chunks=retrieved_chunks,
        category=category,
        history=history_dicts
    )

    # Format response sources
    sources = [
        SourceReference(
            chunk_id=c["chunk_id"],
            document=c["document"],
            section=c["section"],
            text=c["text"],
            score=c["score"]
        )
        for c in retrieved_chunks
    ]

    return ChatResponse(
        answer=llm_result["answer"],
        category=category,
        category_confidence=classification["confidence"],
        matched_keywords=classification["matched_keywords"],
        cleaned_query=cleaned_query,
        has_negation=preprocessed["has_negation"],
        negations_found=preprocessed["negations_found"],
        sources=sources,
        total_sources=len(sources),
        disclaimer=llm_result["disclaimer"],
        model_used=llm_result.get("model_used"),
        is_fallback=llm_result.get("is_fallback", False)
    )

@router.get("/categories")
async def list_healthcare_categories():
    """Returns the list of supported healthcare query categories."""
    return {
        "categories": CATEGORIES,
        "total": len(CATEGORIES)
    }

@router.get("/health")
async def health_check():
    """Backend status check with model and knowledge base readiness."""
    vector_store = get_vector_store()
    stats = vector_store.get_stats()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_model": settings.GROQ_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "knowledge_base": stats
    }

@router.get("/knowledge-base")
async def get_knowledge_base_info():
    """Returns knowledge base statistics and loaded documents."""
    vector_store = get_vector_store()
    return vector_store.get_stats()

