"""
Orchestrator — central coordinator for all user requests (Phase 1).

Pipeline (Phase 1 Hybrid):
  1. Route user input via HybridIntentRouter to an intent and params.
  2. If intent requires a tool -> ToolDispatcher -> format result.
  3. If intent is "conversation" -> LLMRuntime for conversational fallback.

Responsibilities:
- Control flow only
- Coordinate: HybridIntentRouter -> ToolDispatcher -> LLMRuntime (fallback)

Non-responsibilities:
- Intent classification logic
- LLM implementation details
- Tool execution logic
"""

import json

from interfaces.llm_runtime import LLMRuntime, LLMRuntimeError
from routing.intent_router import HybridIntentRouter
from tools.tool_dispatcher import ToolDispatcher, DispatchError


class OrchestratorError(Exception):
    """Raised when the orchestrator pipeline fails unrecoverably."""
    pass


class Orchestrator:
    """
    Coordinate routing, tool dispatch, and conversational fallback.

    Responsibilities:
    - Accept raw user input.
    - Route using HybridIntentRouter.
    - Dispatch tool calls via ToolDispatcher.
    - Fallback to LLMRuntime if intent is conversation.
    - Return final response string.
    """

    def __init__(
        self,
        router: HybridIntentRouter,
        dispatcher: ToolDispatcher,
        runtime: LLMRuntime,
    ) -> None:
        """
        Args:
            router: Resolves user input into an intent.
            dispatcher: Executes tools based on intent.
            runtime: Fallback LLM for conversational responses.
        """
        self._router = router
        self._dispatcher = dispatcher
        self._runtime = runtime

    def handle(self, user_input: str) -> str:
        """
        Handle a single user request through the full Phase 1 pipeline.

        Args:
            user_input: Raw user message text.

        Returns:
            Final response text.
        """
        try:
            route_result = self._router.route(user_input)
        except Exception as exc:
            raise OrchestratorError(f"Routing failed unexpectedly: {exc}") from exc

        if route_result.intent == "conversation":
            return self._handle_conversation(user_input)

        try:
            result = self._dispatcher.dispatch(route_result.intent, route_result.params)
        except DispatchError as exc:
            raise OrchestratorError(f"Tool dispatch failed: {exc}") from exc

        return self._format_tool_result(route_result.intent, result)

    def _handle_conversation(self, user_input: str) -> str:
        """Process conversational fallback using LLM."""
        prompt = (
            "You are a helpful personal assistant. "
            "Please respond to the following user message naturally.\n\n"
            f"User: {user_input}\n"
        )
        try:
            llm_result = self._runtime.run(prompt)
            return llm_result.text
        except LLMRuntimeError as exc:
            raise OrchestratorError("LLM conversational fallback failed") from exc

    @staticmethod
    def _format_tool_result(intent: str, result: dict) -> str:
        """
        Format a tool execution result into a human-readable string.

        Args:
            intent: The name of the tool/intent that was called.
            result: The dict returned by the tool.

        Returns:
            A formatted string suitable for returning to the user.
        """
        return json.dumps(result, ensure_ascii=False, indent=2)
