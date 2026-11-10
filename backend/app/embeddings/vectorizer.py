"""
Lightweight TF-IDF Embedding Engine for CareFlow NLP.

Uses scikit-learn TfidfVectorizer (pure Python/scipy, no ML framework).
Memory footprint: ~20MB total — compatible with Render's free 512MB tier.
No model downloads required at runtime — works fully offline.
"""
import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """
    Text vectorization using TF-IDF with sublinear TF scaling.

    Demonstrates NLP Unit 6 concept of text-to-vector transformation.
    TF-IDF vectors are sparse and interpretable — ideal for structured
    medical domain knowledge retrieval.

    Dimension adapts dynamically based on the vocabulary fitted during indexing.
    For FAISS compatibility, vectors are L2-normalized (unit norm).
    """

    def __init__(self, max_features: int = 4096):
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            sublinear_tf=True,       # Apply log(1+tf) — reduces impact of very frequent terms
            ngram_range=(1, 2),      # Unigrams + bigrams for medical phrase matching
            min_df=1,
            stop_words="english",
            strip_accents="unicode",
            analyzer="word",
        )
        self.dimension: int = max_features  # Will be updated after fit
        self._is_fitted = False
        logger.info(f"TF-IDF EmbeddingEngine initialized (max_features={max_features})")

    def fit(self, texts: List[str]) -> None:
        """Fits the TF-IDF vocabulary on a corpus of documents."""
        self.vectorizer.fit(texts)
        self.dimension = len(self.vectorizer.get_feature_names_out())
        self._is_fitted = True
        logger.info(f"TF-IDF vocabulary fitted: {self.dimension} features from {len(texts)} documents")

    def _to_dense_normalized(self, sparse_matrix) -> np.ndarray:
        """Converts sparse TF-IDF matrix to dense L2-normalized float32 array."""
        dense = sparse_matrix.toarray().astype(np.float32)
        norms = np.linalg.norm(dense, axis=1, keepdims=True)
        norms[norms == 0] = 1e-12
        return dense / norms

    def encode_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """Encodes a single text string into a normalized dense numpy vector."""
        if not self._is_fitted:
            raise RuntimeError("EmbeddingEngine must be fitted before encoding. Call fit() first.")
        sparse = self.vectorizer.transform([text])
        return self._to_dense_normalized(sparse)[0]

    def encode_batch(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Encodes a list of texts into a 2D dense numpy matrix of shape (N, dimension)."""
        if not self._is_fitted:
            raise RuntimeError("EmbeddingEngine must be fitted before encoding. Call fit() first.")
        sparse = self.vectorizer.transform(texts)
        return self._to_dense_normalized(sparse)

    @staticmethod
    def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Calculates cosine similarity between two normalized vectors (inner product)."""
        return float(np.dot(vec_a, vec_b))


_engine_instance = None


def get_embedding_engine() -> EmbeddingEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = EmbeddingEngine()
    return _engine_instance
