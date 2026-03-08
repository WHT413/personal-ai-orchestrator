"""
EmbeddingsProvider — text embedding generation for fast intent routing.

Retrieves and caches a lightweight SentenceTransformer model to map user
input into dense vector representations.
"""

from typing import Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm


class EmbeddingsProvider:
    """
    Wrapper around SentenceTransformer for generating intent embeddings.
    
    Responsibilities:
    - Load and cache the embedding model only when needed.
    - Generate vector representation for a given text.
    - Compute cosine similarity between vectors.
    
    Model chosen: 'paraphrase-multilingual-MiniLM-L12-v2'
    - Supports 50+ languages including Vietnamese and English.
    - Lightweight (~470MB) and very fast for CPU inference.
    """

    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self) -> None:
        self._model: Optional[SentenceTransformer] = None

    def _get_model(self) -> SentenceTransformer:
        """Lazy load the model to save memory until actually used."""
        if self._model is None:
            # Setting device='cpu' to ensure fast deterministic local inference
            # without requiring GPU dependencies unless specified.
            self._model = SentenceTransformer(self.MODEL_NAME, device="cpu")
        return self._model

    def encode(self, text: str) -> np.ndarray:
        """
        Encode a single text string into a dense vector.
        
        Args:
            text: Input string.
            
        Returns:
            1D numpy array representing the embedding.
        """
        model = self._get_model()
        # encode returns a numpy array or tensor; we ensure it's a numpy array.
        return model.encode(text, convert_to_numpy=True)

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """
        Encode multiple strings into a matrix of embeddings.
        
        Args:
            texts: List of input strings.
            
        Returns:
            2D numpy array (num_texts, embedding_dim).
        """
        model = self._get_model()
        return model.encode(texts, convert_to_numpy=True)

    @staticmethod
    def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Compute cosine similarity between two 1D vectors.
        
        Args:
            vec_a: First vector.
            vec_b: Second vector.
            
        Returns:
            Float strictly between -1.0 and 1.0. Higher means more similar.
        """
        if norm(vec_a) == 0 or norm(vec_b) == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (norm(vec_a) * norm(vec_b)))
