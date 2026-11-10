import sys
import os
from pathlib import Path

# Set up paths so we can import from backend/
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.preprocessing import preprocess_query
from app.classification import classify_query
from app.embeddings import get_embedding_engine
from app.retrieval import get_vector_store
from app.llm import get_rag_engine

def run_tests():
    print("=" * 60)
    print("TESTING CAREFLOW NLP BACKEND PIPELINE")
    print("=" * 60)

    # 1. Test Preprocessing
    print("\n--- 1. Testing Text Preprocessing ---")
    query_with_negation = "Patient has dizziness but NO chest pain and without fever."
    proc_res = preprocess_query(query_with_negation)
    print(f"Original: {proc_res['original_query']}")
    print(f"Normalized: {proc_res['normalized_query']}")
    print(f"Tokens: {proc_res['tokens']}")
    print(f"Has Negation: {proc_res['has_negation']} -> Found: {proc_res['negations_found']}")
    assert proc_res["has_negation"] is True, "Failed to detect medical negation"
    assert "no" in proc_res["negations_found"] or "without" in proc_res["negations_found"]
    print("✓ Preprocessing test PASSED!")

    # 2. Test Query Classification
    print("\n--- 2. Testing Healthcare Query Classification ---")
    test_queries = [
        ("What are the classic symptoms of Type 2 diabetes?", "Diabetes"),
        ("What lifestyle changes lower systolic blood pressure?", "Hypertension"),
        ("What are risk factors for coronary artery disease?", "Cardiovascular Health"),
        ("What is the role of dietary fiber and Mediterranean diet?", "Nutrition"),
        ("I feel sharp chest pain, dizziness and shortness of breath.", "Symptoms"),
        ("What are the common side effects of metformin and statins?", "Medication Information"),
        ("How much sleep and water is recommended for general wellness?", "General Healthcare")
    ]

    for q, expected in test_queries:
        cls_res = classify_query(q)
        print(f"Query: '{q[:40]}...' -> Detected: {cls_res['category']} (conf: {cls_res['confidence']}) [Exp: {expected}]")
        assert cls_res["category"] == expected, f"Expected {expected}, got {cls_res['category']}"
    print("✓ Query Classification test PASSED!")

    # 3. Test Embedding Engine
    print("\n--- 3. Testing Embedding Engine ---")
    engine = get_embedding_engine()
    vec = engine.encode_text("Hypertension lifestyle guidelines")
    print(f"Embedding shape: {vec.shape}, norm: {float(sum(vec**2)**0.5):.4f}")
    assert vec.shape[0] == 384, f"Expected 384 dimensions, got {vec.shape[0]}"
    print("✓ Embedding Engine test PASSED!")

    # 4. Test FAISS Vector Store & Retrieval
    print("\n--- 4. Testing FAISS Vector Store & Retrieval ---")
    vs = get_vector_store()
    stats = vs.get_stats()
    print(f"Knowledge Base Stats: {stats}")
    assert stats["total_documents"] >= 5, "Knowledge base did not load all documents"
    assert stats["indexed_vectors"] > 0, "No vectors indexed in FAISS"

    search_query = "What is the difference between Type 1 and Type 2 diabetes?"
    retrieved = vs.search(search_query, top_k=2)
    print(f"Search Query: '{search_query}'")
    print(f"Retrieved {len(retrieved)} chunk(s):")
    for r in retrieved:
        print(f"  • [{r['document']}] {r['section']} (Similarity: {r['score']})")
    assert len(retrieved) > 0, "Retrieval returned empty results"
    assert "diabetes.txt" in [r["document"] for r in retrieved], "Failed to retrieve relevant diabetes document"
    print("✓ FAISS Retrieval test PASSED!")

    # 5. Test Groq LLM & RAG Generation
    print("\n--- 5. Testing Groq LLM Generation & Grounding ---")
    rag = get_rag_engine()
    rag_res = rag.generate_response(
        query=search_query,
        retrieved_chunks=retrieved,
        category="Diabetes"
    )
    print(f"LLM Answer preview:\n{rag_res['answer'][:300]}...")
    print(f"Fallback flag: {rag_res.get('is_fallback')}")
    assert len(rag_res["answer"]) > 50, "Answer too short"
    print("✓ Groq LLM RAG test PASSED!")

    print("\n" + "=" * 60)
    print("ALL NLP BACKEND PIPELINE TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()

