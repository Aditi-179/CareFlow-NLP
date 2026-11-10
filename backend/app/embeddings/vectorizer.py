import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """
    Handles text vectorization using Sentence Transformers.
    Converts arbitrary medical texts and user queries into 384-dimensional dense vectors.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        logger.info(f"Loading Sentence Transformer model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        if hasattr(self.model, "get_embedding_dimension"):
            self.dimension = self.model.get_embedding_dimension()
        else:
            self.dimension = self.model.get_sentence_embedding_dimension()

    def encode_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Encodes a single text string into a normalized numpy vector.
        """
        vector = self.model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        if normalize:
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
        return vector.astype(np.float32)

    def encode_batch(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """
        Encodes a list of text strings into a 2D numpy matrix of shape (N, dimension).
        """
        vectors = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        if normalize:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1e-12
            vectors = vectors / norms
        return vectors.astype(np.float32)

    @staticmethod
    def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Calculates cosine similarity between two normalized vectors."""
        return float(np.dot(vec_a, vec_b))


_engine_instance = None

def get_embedding_engine() -> EmbeddingEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = EmbeddingEngine()
    return _engine_instance

