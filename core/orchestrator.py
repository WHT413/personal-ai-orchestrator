"""
Orchestrator — central coordinator for all user requests.

Pipeline (Phase 1):
  1. Build a tool-aware prompt
  2. Run LLM inference
  3. Parse LLM output for a structured tool call
  4. If tool call found → dispatch deterministically → format result
  5. If no tool call → return LLM text as conversational response

Responsibilities:
- Control flow only
- Coordinate: PromptBuilder → LLMRuntime → IntentParser → ToolDispatcher

Non-responsibilities:
- LLM implementation details
- Tool logic
- Prompt strategy
"""

import json

from interfaces.llm_runtime import LLMRuntime, LLMRuntimeError
from core.prompt_builder import PromptBuilder
from core.intent_parser import IntentParser, ParseError
from core.tool_dispatcher import ToolDispatcher, DispatchError


class OrchestratorError(Exception):
    """
    Raised when the orchestrator pipeline fails unrecoverably.
    """
    pass


class Orchestrator:
    """
    Coordinate prompt building, LLM execution, intent parsing, and tool dispatch.

    Responsibilities:
    - Accept user input
    - Build prompt via PromptBuilder
    - Execute LLM runtime
    - Parse LLM output for tool call intent
    - Dispatch tool calls via ToolDispatcher
    - Return final response string

    Non-responsibilities:
    - LLM implementation details
    - Tool business logic
    - Retry or fallback policies
    """

    def __init__(
        self,
        runtime: LLMRuntime,
        prompt_builder: PromptBuilder,
        dispatcher: ToolDispatcher,
        intent_parser: IntentParser,
    ) -> None:
        """
        Args:
            runtime: LLM runtime to execute prompts.
            prompt_builder: Builds the prompt from user input.
            dispatcher: Dispatches resolved tool calls.
            intent_parser: Parses LLM output for tool call intent.
        """
        self._runtime = runtime
        self._prompt_builder = prompt_builder
        self._dispatcher = dispatcher
        self._intent_parser = intent_parser

    def handle(self, user_input: str) -> str:
        """
        Handle a single user request through the full pipeline.

        Contract:
        - One input, one output string
        - Blocking call
        - Raises OrchestratorError on unrecoverable failure

        Args:
            user_input: Raw user input text.

        Returns:
            Final response text.
        """
        try:
            prompt = self._prompt_builder.build(user_input)
            llm_result = self._runtime.run(prompt)
        except LLMRuntimeError as exc:
            raise OrchestratorError("LLM runtime failed") from exc
        except Exception as exc:
            raise OrchestratorError("Unexpected error during LLM execution") from exc

        try:
            tool_call = self._intent_parser.parse(llm_result.text)
        except ParseError as exc:
            raise OrchestratorError(f"Failed to parse LLM output: {exc}") from exc

        if tool_call is None:
            # Conversational response — no tool required
            return llm_result.text

        try:
            result = self._dispatcher.dispatch(tool_call)
        except DispatchError as exc:
            raise OrchestratorError(f"Tool dispatch failed: {exc}") from exc

        return self._format_tool_result(tool_call.tool, result)

    @staticmethod
    def _format_tool_result(tool_name: str, result: dict) -> str:
        """
        Format a tool execution result into a human-readable string.

        Args:
            tool_name: The name of the tool that was called.
            result: The dict returned by the tool.

        Returns:
            A formatted string suitable for returning to the user.
        """
        return json.dumps(result, ensure_ascii=False, indent=2)
