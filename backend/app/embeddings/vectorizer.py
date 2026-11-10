import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """
    Handles text vectorization using fastembed (ONNX-based, ~50MB RAM).
    Converts arbitrary medical texts and user queries into 384-dimensional dense vectors.
    Uses BAAI/bge-small-en-v1.5 — lightweight and accurate, no PyTorch dependency.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        from fastembed import TextEmbedding
        logger.info(f"Loading fastembed model: {model_name}")
        self.model = TextEmbedding(model_name=model_name)
        self.dimension = 384  # bge-small-en-v1.5 outputs 384-d vectors
        self._model_name = model_name

    def encode_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """Encodes a single text string into a normalized numpy vector."""
        embeddings = list(self.model.embed([text]))
        vec = np.array(embeddings[0], dtype=np.float32)
        if normalize:
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
        return vec

    def encode_batch(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Encodes a list of text strings into a 2D numpy matrix of shape (N, dimension)."""
        embeddings = list(self.model.embed(texts))
        matrix = np.array(embeddings, dtype=np.float32)
        if normalize:
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1e-12
            matrix = matrix / norms
        return matrix

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

