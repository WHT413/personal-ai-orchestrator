"""
IntentRouter — Hybrid Intent Router (Phase 1).

Determines which tool (or conversation fallback) should handle a user request
using a "fast path" (Embedding Similarity) and a "slow path" (LLM Classification).

 Intents (Phase 1):
  - finance.add_expense
  - finance.query_expenses
  - calendar.create_event
  - calendar.list_events
  - conversation (Fallback)

 Non-responsibilities:
 - Parameter extraction (To be handled by the tool logic receiving the raw input)
 - Executing tools
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

from interfaces.llm_runtime import LLMRuntime
from routing.embeddings import EmbeddingsProvider


@dataclass
class RouteResult:
    """
    Result of intent routing.

    Attributes:
        intent: Dot-notation intent name (e.g. 'finance.add_expense').
        params: Raw user input passed down for the tool to digest.
    """
    intent: str
    params: dict


class HybridIntentRouter:
    """
    Route user input to an intent using Embeddings first, LLM Fallback second.

    Contract:
    - Fast path computes cosine similarity of `user_input` against predefined examples.
    - If max similarity >= `confidence_threshold`, returns the matching intent.
    - If max similarity < `confidence_threshold`, calls LLM to classify.
    - Always parses input as raw text in `params` for downstream extraction.
    - Any error or unparseable state defaults to "conversation".
    """

    # Pre-defined intent examples for the Embedding fast-path
    _INTENT_EXAMPLES: Dict[str, List[str]] = {
        "finance.add_expense": [
            "thêm chi tiêu 50k",
            "chi 100k tiền ăn",
            "add expense 50000 for food",
            "ghi nhận 20k cafe hôm nay",
            "mua đồ mất 500k",
        ],
        "finance.query_expenses": [
            "xem chi tiêu",
            "liệt kê chi tiêu",
            "list my expenses",
            "hôm nay tiêu bao nhiêu tiền",
            "báo cáo tài chính",
        ],
        "calendar.create_event": [
            "tạo lịch họp 9h sáng mai",
            "thêm sự kiện mới",
            "add a meeting tomorrow",
            "đặt lịch cafe với bạn",
            "schedule an event",
        ],
        "calendar.list_events": [
            "xem lịch hôm nay",
            "lịch trình ngày mai",
            "show my calendar",
            "có họp gì không",
            "list events",
        ],
        "conversation": [
            "chào bạn, bạn khỏe không",
            "thời tiết hôm nay thế nào",
            "kể chuyện cười đi",
            "giúp tôi viết code",
            "ai là tổng thống mỹ",
        ]
    }

    _LLM_PROMPT_TEMPLATE = (
        "You are an intent classification system. Determine the correct intent "
        "for the user's message. Choose ONLY ONE from the following list:\n"
        "- finance.add_expense\n"
        "- finance.query_expenses\n"
        "- calendar.create_event\n"
        "- calendar.list_events\n"
        "- conversation\n\n"
        "User message: {user_input}\n\n"
        "Reply ONLY with a structured JSON format like this:\n"
        '{{"intent": "finance.add_expense"}}'
    )

    def __init__(
        self,
        embedding_provider: EmbeddingsProvider,
        llm_runtime: LLMRuntime,
        confidence_threshold: float = 0.8
    ) -> None:
        """
        Initialize the router and pre-compute embeddings for fast-path.
        
        Args:
            embedding_provider: Instantiated EmbeddingsProvider.
            llm_runtime: The LLM backend for fallback classification.
            confidence_threshold: Cosine similarity threshold (0.0 to 1.0).
        """
        self._provider = embedding_provider
        self._llm = llm_runtime
        self._threshold = confidence_threshold

        # Cache reference embeddings: intent -> list of vectors
        self._reference_embeddings: Dict[str, List[np.ndarray]] = {}
        for intent, examples in self._INTENT_EXAMPLES.items():
            self._reference_embeddings[intent] = [
                self._provider.encode(ex) for ex in examples
            ]

    def route(self, user_input: str) -> RouteResult:
        """
        Determine intent. Fast path first, LLM fallback if uncertain.
        
        Args:
            user_input: Raw text from the user.
            
        Returns:
            RouteResult with the chosen intent and params={"user_input": ...}
        """
        text = user_input.strip()
        if not text:
            return RouteResult(intent="conversation", params={"user_input": text})

        # 1. Fast Path: Embedding Similarity
        try:
            target_vec = self._provider.encode(text)
            best_intent = "conversation"
            best_score = -1.0

            for intent, vectors in self._reference_embeddings.items():
                for ref_vec in vectors:
                    score = self._provider.cosine_similarity(target_vec, ref_vec)
                    if score > best_score:
                        best_score, best_intent = score, intent
            
            # Fast-path succeeds if confident enough
            if best_score >= self._threshold:
                return RouteResult(
                    intent=best_intent,
                    params={"user_input": text}
                )

        except Exception:
            # If embeddings fail (e.g., model failed to load), fallback gracefully to LLM
            pass

        # 2. Slow Path: LLM Fallback Classification
        try:
            prompt = self._LLM_PROMPT_TEMPLATE.format(user_input=text)
            llm_result = self._llm.run(prompt)
            
            # Extract JSON from the raw LLM output
            parsed = self._parse_json_fallback(llm_result.text)
            if parsed and parsed.get("intent") in self._INTENT_EXAMPLES:
                return RouteResult(
                    intent=parsed["intent"],
                    params={"user_input": text}
                )
        except Exception:
            pass

        # Ultimate fallback
        return RouteResult(intent="conversation", params={"user_input": text})

    def _parse_json_fallback(self, text: str) -> Optional[dict]:
        """Attempt to parse a single JSON object from LLM output."""
        text = text.strip()
        
        # Simple heuristic to extract text between first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
        return None
