import re
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
    Synthesizes evidence from local FAISS clinical docs, live web searches,
    and parsed medical laboratory reports.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        if not self.api_key:
            logger.warning("GROQ_API_KEY is not configured.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)

    def clean_text_formatting(self, text: str) -> str:
        """Cleans accidental HTML <br> or messy formatting from model output."""
        if not text:
            return ""
        # Replace <br> or <br/> with newline
        cleaned = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        # Clean extra blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def generate_response(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        category: str,
        history: Optional[List[Dict[str, str]]] = None,
        web_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes a clinically grounded response using Groq LLM with a warm, natural tone.
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
        context_blocks = []
        if retrieved_chunks:
            for i, chunk in enumerate(retrieved_chunks, 1):
                doc_name = chunk.get("document", "Clinical Reference")
                sec_name = chunk.get("section", "General Section")
                score = chunk.get("score", 0.0)
                text = chunk.get("text", "").strip()
                context_blocks.append(
                    f"[Local Doc {i}: {doc_name} | {sec_name} (Similarity: {score:.2f})]\n{text}"
                )

        # Inject Live Web Search context if present
        if web_results:
            for j, web in enumerate(web_results, 1):
                title = web.get("title", "Web Reference")
                url = web.get("url", "")
                snippet = web.get("snippet", "").strip()
                context_blocks.append(
                    f"[Web Search {j}: {title} | Source: {url}]\n{snippet}"
                )

        if context_blocks:
            context_str = "\n\n".join(context_blocks)
        else:
            context_str = "No specific clinical documents met the similarity threshold in the local knowledge base."

        # Construct Natural Clinical System Prompt
        system_prompt = f"""You are CareFlow NLP, an intelligent, empathetic, and evidence-based healthcare educator.
Your purpose is to answer health questions with accuracy, warmth, and clarity, making complex medical facts easy to understand.

### DETECTED QUERY TOPIC:
{category}

### RETRIEVED EVIDENCE & REFERENCES (GROUND YOUR ANSWER HERE):
---
{context_str}
---

### COMMUNICATION & FORMATTING GUIDELINES:
1. Tone: Warm, reassuring, clear, and professional. Write like a thoughtful clinical specialist speaking directly to a patient.
2. Structure:
   - Start with a direct, encouraging 1–2 sentence answer.
   - Use clean, readable bullet points with bold lead-ins for key points (e.g., "**DASH Diet:** Focus on fruits, vegetables...").
   - DO NOT dump dense ASCII pipe tables with `<br>` tags. Write natural paragraphs and bullet lists instead.
3. Grounding & Citations:
   - Reference source documents naturally (e.g. "According to clinical guidelines in *hypertension.txt*..." or "[hypertension.txt]").
   - If web search results are included, reference them with clickable markdown links where helpful.
4. Medical Safety:
   - If the patient describes acute warning signs (such as crushing chest pain or severe breathlessness), explicitly urge immediate emergency medical care.
   - Never prescribe specific medication dosages or claim to make a definitive diagnosis.
"""

        messages = [{"role": "system", "content": system_prompt}]

        # Inject active history (up to last 6 messages)
        if history:
            for msg in history[-6:]:
                role = msg.get("role")
                content = msg.get("content")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": query})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.25,
                max_tokens=1024,
            )
            raw_answer = response.choices[0].message.content.strip()
            clean_answer = self.clean_text_formatting(raw_answer)

            return {
                "answer": clean_answer,
                "is_fallback": False,
                "disclaimer": DISCLAIMER_TEXT,
                "model_used": self.model
            }

        except Exception as e:
            logger.error(f"Groq API inference failed: {e}")
            fallback_text = (
                f"We retrieved relevant information from the knowledge base, but encountered an issue with AI generation ({str(e)}).\n\n"
                "**Summary of Retrieved Evidence:**\n"
            )
            for chunk in retrieved_chunks:
                fallback_text += f"* **{chunk['document']}** ({chunk['section']}): {chunk['text'][:160]}...\n"

            return {
                "answer": fallback_text,
                "is_fallback": True,
                "disclaimer": DISCLAIMER_TEXT,
                "error": str(e)
            }

    def analyze_report(
        self,
        report_text: str,
        biomarkers: List[Dict[str, Any]],
        category: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Performs in-depth clinical analysis of an uploaded medical lab report.
        """
        if not self.client:
            return {
                "summary": "AI inference client not configured. Extracted lab markers are shown below.",
                "disclaimer": DISCLAIMER_TEXT
            }

        # Format biomarkers summary
        markers_str = ""
        if biomarkers:
            for m in biomarkers:
                markers_str += f"- {m['name']}: {m['value']} {m['unit']} (Normal Range: {m['normal_range']}) -> Status: {m['status'].upper()}\n"
        else:
            markers_str = "No standard numerical lab markers were automatically matched in the text."

        # Knowledge context
        kb_context = "\n".join([f"[{c['document']} - {c['section']}]: {c['text'][:300]}" for c in retrieved_chunks])

        prompt = f"""You are CareFlow NLP analyzing an uploaded patient medical lab report.

### EXTRACTED LAB BIOMARKERS:
{markers_str}

### RAW REPORT CONTENT (EXCERPT):
{report_text[:1800]}

### CLINICAL GUIDELINE CONTEXT:
{kb_context}

Please provide a compassionate, clear, and structured medical report interpretation:
1. **Executive Summary:** A warm, plain-English overview of the report's general picture.
2. **Key Biomarker Breakdown:** Explain what the abnormal or borderline values mean in everyday terms without medical jargon.
3. **Evidence-Based Lifestyle Recommendations:** Suggest evidence-based dietary or daily routine adjustments (referencing guidelines).
4. **Questions for Your Doctor:** 3–4 specific, practical questions the patient can take to their next healthcare provider appointment.

Remember: Do NOT diagnose disease or prescribe drug dosages. Be reassuring and clear."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are CareFlow NLP, an expert medical report analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1200
            )
            raw = response.choices[0].message.content.strip()
            cleaned = self.clean_text_formatting(raw)
            return {
                "summary": cleaned,
                "disclaimer": DISCLAIMER_TEXT,
                "model_used": self.model
            }
        except Exception as e:
            logger.error(f"Report analysis error: {e}")
            return {
                "summary": f"Analyzed {len(biomarkers)} biomarker parameters from your report. Detailed AI explanation unavailable ({str(e)}).",
                "disclaimer": DISCLAIMER_TEXT
            }


_rag_engine_instance = None

def get_rag_engine() -> GroqRAGEngine:
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = GroqRAGEngine()
    return _rag_engine_instance
