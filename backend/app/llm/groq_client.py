from typing import List, Dict, Any, Optional
from groq import Groq
from app.config import settings
import logging

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "Disclaimer: CareFlow NLP is an educational healthcare query understanding system. "
    "It is not a diagnostic tool and does not provide formal medical advice or prescription dosages. "
    "In the event of an acute emergency, please contact local emergency medical services immediately."
)

class GroqRAGEngine:
    """
    Retrieval-Augmented Generation (RAG) Orchestrator using Groq LLM.
    Grounds LLM generation directly upon retrieved FAISS clinical excerpts.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        if not self.api_key:
            logger.warning("GROQ_API_KEY is not configured.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)

    def generate_response(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        category: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes a clinically grounded response using Groq LLM.
        """
        if not self.client:
            return {
                "answer": (
                    "Groq API key is not configured on the server. Please set GROQ_API_KEY in your environment. "
                    f"Retrieved {len(retrieved_chunks)} relevant source document(s) matching your query."
                ),
                "is_fallback": True,
                "disclaimer": DISCLAIMER_TEXT
            }

        # Build context string from retrieved chunks
        if retrieved_chunks:
            context_blocks = []
            for i, chunk in enumerate(retrieved_chunks, 1):
                doc_name = chunk.get("document", "Unknown Document")
                sec_name = chunk.get("section", "General Section")
                score = chunk.get("score", 0.0)
                text = chunk.get("text", "").strip()
                context_blocks.append(
                    f"[Source {i} | Document: {doc_name} | Section: {sec_name} | Relevance: {score:.2f}]\n{text}"
                )
            context_str = "\n\n".join(context_blocks)
        else:
            context_str = "No specific clinical documents met the similarity threshold in the local knowledge base."

        # Construct System Prompt grounded in medical safety
        system_prompt = f"""You are CareFlow NLP, an intelligent, evidence-based healthcare query understanding assistant.
Your goal is to provide clear, accurate, and understandable healthcare answers grounded in the provided clinical reference documents.

### IDENTIFIED QUERY CATEGORY:
{category}

### RETRIEVED CLINICAL KNOWLEDGE (USE THIS FACTUAL EVIDENCE):
---
{context_str}
---

### STRICT CLINICAL & OPERATIONAL RULES:
1. Ground your answer primarily on the retrieved clinical reference documents above.
2. Cite the source document names (e.g. [diabetes.txt], [hypertension.txt]) naturally when discussing their points.
3. If the retrieved context does not contain sufficient details to answer the query, clearly state the limitation instead of fabricating medical facts or prescribing unverified remedies.
4. If the user presents red-flag emergency symptoms (such as acute crushing chest pain, sudden slurred speech, severe shortness of breath), advise them to seek immediate emergency medical care.
5. Do NOT prescribe individual drug dosages or replace a licensed physician's clinical diagnosis.
6. Provide concise, structured, and compassionate explanations using bullet points and clear paragraphs.
"""

        # Build message chain
        messages = [{"role": "system", "content": system_prompt}]

        # Inject recent active conversation history (up to last 6 messages)
        if history:
            for msg in history[-6:]:
                role = msg.get("role")
                content = msg.get("content")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})

        # Append current user prompt
        messages.append({"role": "user", "content": query})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2, # Low temperature for factual, reliable medical response
                max_tokens=1024,
            )
            generated_answer = response.choices[0].message.content.strip()

            return {
                "answer": generated_answer,
                "is_fallback": False,
                "disclaimer": DISCLAIMER_TEXT,
                "model_used": self.model
            }

        except Exception as e:
            logger.error(f"Groq API inference failed: {e}")
            # Graceful degradation fallback
            fallback_text = (
                f"We retrieved relevant information from the knowledge base, but encountered an issue connecting to the AI inference service ({str(e)}).\n\n"
                "Summary of retrieved sources:\n"
            )
            for chunk in retrieved_chunks:
                fallback_text += f"• **{chunk['document']}** ({chunk['section']}): {chunk['text'][:150]}...\n"

            return {
                "answer": fallback_text,
                "is_fallback": True,
                "disclaimer": DISCLAIMER_TEXT,
                "error": str(e)
            }


_rag_engine_instance = None

def get_rag_engine() -> GroqRAGEngine:
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = GroqRAGEngine()
    return _rag_engine_instance

