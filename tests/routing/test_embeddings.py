"""Unit tests for EmbeddingsProvider."""

import numpy as np
from routing.embeddings import EmbeddingsProvider


def test_cosine_similarity_identical_vectors():
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([1.0, 0.0, 0.0])
    score = EmbeddingsProvider.cosine_similarity(vec_a, vec_b)
    # Floating point precision might make it 0.9999999
    assert score > 0.99


def test_cosine_similarity_orthogonal_vectors():
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([0.0, 1.0, 0.0])
    score = EmbeddingsProvider.cosine_similarity(vec_a, vec_b)
    assert abs(score) < 1e-6


def test_cosine_similarity_opposite_vectors():
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([-1.0, 0.0, 0.0])
    score = EmbeddingsProvider.cosine_similarity(vec_a, vec_b)
    assert score < -0.99


def test_cosine_similarity_zero_vector_returns_zero():
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([0.0, 0.0, 0.0])
    score = EmbeddingsProvider.cosine_similarity(vec_a, vec_b)
    assert score == 0.0
