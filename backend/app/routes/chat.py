from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel, Field

from app.config import settings
from app.preprocessing import preprocess_query
from app.classification import classify_query, CATEGORIES
from app.retrieval import get_vector_store
from app.retrieval.web_search import search_medical_web
from app.retrieval.report_parser import extract_text_from_file, parse_lab_biomarkers
from app.llm import get_rag_engine

router = APIRouter(prefix="/api", tags=["Healthcare Chatbot & NLP"])

class ChatHistoryMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000, description="User healthcare query")
    history: Optional[List[ChatHistoryMessage]] = Field(default=[], description="Active conversation session history")
    enable_web_search: Optional[bool] = Field(default=False, description="Enable live web search augmentation")

class SourceReference(BaseModel):
    chunk_id: Optional[int] = None
    document: str
    section: str
    text: str
    score: float
    source_type: str = "local"
    url: Optional[str] = None

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
    web_searched: bool = False

class BiomarkerItem(BaseModel):
    name: str
    value: str
    unit: str
    normal_range: str
    status: str

class ReportAnalysisResponse(BaseModel):
    filename: str
    summary: str
    category: str
    biomarkers: List[BiomarkerItem]
    sources: List[SourceReference]
    disclaimer: str
    model_used: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def process_healthcare_query(payload: ChatRequest):
    """
    Enhanced RAG Endpoint:
    1. Text Preprocessing (Tokenization, Negation Preservation, Noise Reduction)
    2. Query Intent Classification
    3. Dense Vector Semantic Search via FAISS
    4. Optional Live Medical Web Search Augmentation
    5. Natural Grounded Response Generation with Groq LLM
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

    # 4. Optional Live Web Search
    web_results = []
    web_searched = False
    if payload.enable_web_search or len(retrieved_chunks) == 0:
        web_results = search_medical_web(raw_query, max_results=3)
        web_searched = len(web_results) > 0

    # 5. LLM Generation via Groq
    rag_engine = get_rag_engine()
    history_dicts = [h.model_dump() for h in payload.history] if payload.history else []
    
    llm_result = rag_engine.generate_response(
        query=raw_query,
        retrieved_chunks=retrieved_chunks,
        category=category,
        history=history_dicts,
        web_results=web_results
    )

    # Format local and web sources
    sources = []
    for c in retrieved_chunks:
        sources.append(SourceReference(
            chunk_id=c.get("chunk_id"),
            document=c["document"],
            section=c["section"],
            text=c["text"],
            score=c["score"],
            source_type="local"
        ))
    for w in web_results:
        sources.append(SourceReference(
            chunk_id=None,
            document=w["title"],
            section="Live Web Medical Knowledge",
            text=w["snippet"],
            score=0.90,
            source_type="web",
            url=w["url"]
        ))

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
        is_fallback=llm_result.get("is_fallback", False),
        web_searched=web_searched
    )

@router.post("/upload-report", response_model=ReportAnalysisResponse)
async def upload_medical_report(file: UploadFile = File(...)):
    """
    Medical Lab Report Ingestion & NLP Analysis:
    1. Extracts text from uploaded PDF or text file
    2. Identifies clinical biomarkers and compares against reference ranges
    3. Categorizes primary domain
    4. Retrieves guideline context from FAISS
    5. Synthesizes an empathetic, plain-language patient report analysis
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    # 1. Extract text from PDF / text file
    extracted_text = extract_text_from_file(file.filename, contents)
    if not extracted_text or len(extracted_text.strip()) < 10:
        extracted_text = f"Report file: {file.filename}. (Text could not be extracted directly from this format)."

    # 2. Parse clinical biomarkers
    biomarkers_raw = parse_lab_biomarkers(extracted_text)

    # 3. Classify report category
    preproc = preprocess_query(extracted_text[:1000])
    classification = classify_query(extracted_text[:1000], preproc["informative_tokens"])
    category = classification["category"]

    # 4. Retrieve matching clinical guidelines
    vector_store = get_vector_store()
    retrieved_chunks = vector_store.search(
        query=f"{category} laboratory guidelines biomarkers",
        top_k=2
    )

    # 5. Generate LLM Analysis
    rag_engine = get_rag_engine()
    analysis = rag_engine.analyze_report(
        report_text=extracted_text,
        biomarkers=biomarkers_raw,
        category=category,
        retrieved_chunks=retrieved_chunks
    )

    biomarker_items = [
        BiomarkerItem(
            name=b["name"],
            value=b["value"],
            unit=b["unit"],
            normal_range=b["normal_range"],
            status=b["status"]
        )
        for b in biomarkers_raw
    ]

    sources = [
        SourceReference(
            chunk_id=c.get("chunk_id"),
            document=c["document"],
            section=c["section"],
            text=c["text"],
            score=c["score"],
            source_type="local"
        )
        for c in retrieved_chunks
    ]

    return ReportAnalysisResponse(
        filename=file.filename,
        summary=analysis["summary"],
        category=category,
        biomarkers=biomarker_items,
        sources=sources,
        disclaimer=analysis["disclaimer"],
        model_used=analysis.get("model_used")
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
