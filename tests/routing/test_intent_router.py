"""Unit tests for HybridIntentRouter."""

import pytest
import numpy as np
from unittest.mock import MagicMock

from interfaces.llm_runtime import LLMRuntime, LLMResult
from routing.embeddings import EmbeddingsProvider
from routing.intent_router import HybridIntentRouter


@pytest.fixture
def mock_embeddings():
    provider = MagicMock(spec=EmbeddingsProvider)
    # Give target the same exact mock embedding so similarity = 1.0 (fast path hits)
    provider.encode.return_value = np.array([1.0, 0.0])
    provider.cosine_similarity.return_value = 1.0
    return provider


@pytest.fixture
def mock_llm():
    llm = MagicMock(spec=LLMRuntime)
    return llm


def test_fast_path_routing_success(mock_embeddings, mock_llm):
    # Confidence threshold 0.8. Our mock similarity returns 1.0 safely.
    router = HybridIntentRouter(mock_embeddings, mock_llm, confidence_threshold=0.8)
    
    # In reality, it compares user_input to ALL cached intents and takes the first match
    # Since mock always returns 1.0, it will just pick the first intent in the dictionary.
    # To test actual logic, let's fix similarity:
    def fake_sim(tgt, ref):
        # We'll tag ref vectors by their text length for testing
        return 0.99
        
    mock_embeddings.cosine_similarity.side_effect = fake_sim
    
    result = router.route("thêm chi tiêu")
    
    # LLM should never be called
    mock_llm.run.assert_not_called()
    assert result.intent is not None
    assert result.params["user_input"] == "thêm chi tiêu"


def test_slow_path_llm_fallback(mock_embeddings, mock_llm):
    # Force fast-path to fail
    mock_embeddings.cosine_similarity.return_value = 0.1
    
    mock_llm.run.return_value = LLMResult(
        text='Here is the result:\n{"intent": "finance.query_expenses"}',
        elapsed_ms=100
    )
    
    router = HybridIntentRouter(mock_embeddings, mock_llm, confidence_threshold=0.8)
    result = router.route("hôm qua tôi xài bao nhiêu?")
    
    # LLM should have been called
    mock_llm.run.assert_called_once()
    assert result.intent == "finance.query_expenses"


def test_slow_path_llm_fallback_invalid_json(mock_embeddings, mock_llm):
    # Force fast-path to fail
    mock_embeddings.cosine_similarity.return_value = 0.1
    
    mock_llm.run.return_value = LLMResult(
        text='I am just chatting normally.',
        elapsed_ms=100
    )
    
    router = HybridIntentRouter(mock_embeddings, mock_llm, confidence_threshold=0.8)
    result = router.route("xin chào")
    
    mock_llm.run.assert_called_once()
    assert result.intent == "conversation"


def test_empty_string_routes_to_conversation(mock_embeddings, mock_llm):
    router = HybridIntentRouter(mock_embeddings, mock_llm, confidence_threshold=0.8)
    mock_embeddings.encode.reset_mock()
    
    result = router.route("")
    
    mock_embeddings.encode.assert_not_called()
    mock_llm.run.assert_not_called()
    assert result.intent == "conversation"
