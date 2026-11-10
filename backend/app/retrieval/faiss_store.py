import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from app.config import settings
from app.embeddings.vectorizer import get_embedding_engine
import logging

logger = logging.getLogger(__name__)

class DocumentChunk:
    def __init__(self, document: str, section: str, text: str, chunk_id: int):
        self.document = document
        self.section = section
        self.text = text
        self.chunk_id = chunk_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document": self.document,
            "section": self.section,
            "text": self.text
        }


class FAISSVectorStore:
    """
    Knowledge Base Ingestion, Chunking, and FAISS Vector Search Engine.
    """

    def __init__(self, kb_dir: Optional[str] = None):
        self.kb_dir = Path(kb_dir or settings.KNOWLEDGE_BASE_DIR)
        self.embedding_engine = get_embedding_engine()
        self.dimension = self.embedding_engine.dimension
        # IndexFlatIP calculates inner product (cosine similarity for normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks: List[DocumentChunk] = []
        self.is_indexed = False

    def chunk_document(self, filename: str, content: str) -> List[DocumentChunk]:
        """
        Splits medical document into semantic chunks using headings and paragraphs.
        Preserves section titles and contextual hierarchy.
        """
        chunks: List[DocumentChunk] = []
        lines = content.splitlines()

        current_section = "General Overview"
        current_buffer = []

        for line in lines:
            stripped = line.strip()
            # Match Markdown headers like ## 2. Symptoms
            if stripped.startswith("## ") or stripped.startswith("# "):
                if current_buffer:
                    chunk_text = "\n".join(current_buffer).strip()
                    if len(chunk_text) > 40:
                        chunks.append(DocumentChunk(
                            document=filename,
                            section=current_section,
                            text=chunk_text,
                            chunk_id=len(chunks)
                        ))
                    current_buffer = []
                current_section = stripped.lstrip("#").strip()
            else:
                if stripped:
                    current_buffer.append(stripped)

        # Flush trailing content
        if current_buffer:
            chunk_text = "\n".join(current_buffer).strip()
            if len(chunk_text) > 40:
                chunks.append(DocumentChunk(
                    document=filename,
                    section=current_section,
                    text=chunk_text,
                    chunk_id=len(chunks)
                ))

        return chunks

    def build_index(self, force_reload: bool = False) -> int:
        """
        Reads all text files from knowledge_base directory, generates embeddings,
        and constructs the FAISS search index.
        """
        if self.is_indexed and not force_reload:
            return len(self.chunks)

        if not self.kb_dir.exists():
            logger.warning(f"Knowledge base directory does not exist: {self.kb_dir}")
            return 0

        self.chunks = []
        doc_files = list(self.kb_dir.glob("*.txt"))
        logger.info(f"Indexing {len(doc_files)} knowledge base files from {self.kb_dir}")

        for doc_path in sorted(doc_files):
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                file_chunks = self.chunk_document(doc_path.name, content)
                self.chunks.extend(file_chunks)
            except Exception as e:
                logger.error(f"Error reading {doc_path}: {e}")

        # Re-assign sequential chunk IDs
        for i, chunk in enumerate(self.chunks):
            chunk.chunk_id = i

        if not self.chunks:
            logger.warning("No document chunks created.")
            return 0

        # Generate embeddings for all chunks in batch
        texts = [f"{c.section}\n{c.text}" for c in self.chunks]
        embeddings = self.embedding_engine.encode_batch(texts, normalize=True)

        # Build fresh FAISS Index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)
        self.is_indexed = True

        logger.info(f"FAISS index built successfully with {self.index.ntotal} vectors.")
        return len(self.chunks)

    def search(self, query: str, top_k: int = 3, threshold: float = 0.20) -> List[Dict[str, Any]]:
        """
        Encodes user query, performs vector similarity search in FAISS,
        and returns top scoring document excerpts with metadata.
        """
        if not self.is_indexed or self.index.ntotal == 0:
            self.build_index()

        if self.index.ntotal == 0:
            return []

        query_vector = self.embedding_engine.encode_text(query, normalize=True)
        query_batch = np.expand_dims(query_vector, axis=0)

        # Retrieve top_k candidates
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_batch, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            if score >= threshold:
                chunk = self.chunks[idx]
                results.append({
                    "chunk_id": chunk.chunk_id,
                    "document": chunk.document,
                    "section": chunk.section,
                    "text": chunk.text,
                    "score": round(float(score), 4)
                })

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Returns knowledge base indexing statistics."""
        docs = set(c.document for c in self.chunks)
        return {
            "total_documents": len(docs),
            "documents": sorted(list(docs)),
            "total_chunks": len(self.chunks),
            "indexed_vectors": self.index.ntotal if self.is_indexed else 0,
            "dimension": self.dimension
        }


_vector_store_instance = None

def get_vector_store() -> FAISSVectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = FAISSVectorStore()
        _vector_store_instance.build_index()
    return _vector_store_instance

