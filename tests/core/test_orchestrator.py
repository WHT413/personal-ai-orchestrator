"""Unit tests for Orchestrator (tool-wired pipeline)."""

import json
import pytest
from unittest.mock import MagicMock, patch

from interfaces.llm_runtime import LLMRuntime, LLMResult, LLMRuntimeError
from core.orchestrator import Orchestrator, OrchestratorError
from core.prompt_builder import PromptBuilder
from core.intent_parser import IntentParser, ToolCall, ParseError
from core.tool_dispatcher import ToolDispatcher, DispatchError


def make_orchestrator(llm_text: str, tool_call: ToolCall | None = None, tool_result: dict | None = None):
    """Helper to build a fully mocked Orchestrator."""
    runtime = MagicMock(spec=LLMRuntime)
    runtime.run.return_value = LLMResult(text=llm_text, elapsed_ms=10)

    prompt_builder = MagicMock(spec=PromptBuilder)
    prompt_builder.build.return_value = "mocked prompt"

    parser = MagicMock(spec=IntentParser)
    parser.parse.return_value = tool_call

    dispatcher = MagicMock(spec=ToolDispatcher)
    if tool_result is not None:
        dispatcher.dispatch.return_value = tool_result

    return Orchestrator(
        runtime=runtime,
        prompt_builder=prompt_builder,
        dispatcher=dispatcher,
        intent_parser=parser,
    )


# ── conversational path ────────────────────────────────────────────────────────

def test_handle_returns_llm_text_when_no_tool_call():
    orc = make_orchestrator(llm_text="Hello! How can I help?", tool_call=None)
    result = orc.handle("hi")
    assert result == "Hello! How can I help?"


def test_handle_does_not_dispatch_when_no_tool_call():
    orc = make_orchestrator(llm_text="Hello!", tool_call=None)
    orc.handle("hi")
    orc._dispatcher.dispatch.assert_not_called()


# ── tool dispatch path ─────────────────────────────────────────────────────────

def test_handle_dispatches_tool_when_tool_call_detected():
    tool_call = ToolCall(tool="finance.add_expense", args={"amount": 50000})
    tool_result = {"id": "abc", "amount": 50000, "category": "food"}
    orc = make_orchestrator(llm_text="TOOL_CALL: ...", tool_call=tool_call, tool_result=tool_result)

    result = orc.handle("ghi 50k com")

    orc._dispatcher.dispatch.assert_called_once_with(tool_call)
    # Result should be JSON-formatted tool result
    parsed = json.loads(result)
    assert parsed == tool_result


def test_handle_formats_tool_result_as_json():
    tool_call = ToolCall(tool="finance.query_expenses", args={})
    tool_result = {"expenses": []}
    orc = make_orchestrator(llm_text="TOOL_CALL: ...", tool_call=tool_call, tool_result=tool_result)
    result = orc.handle("list expenses")
    assert json.loads(result) == {"expenses": []}


# ── error paths ────────────────────────────────────────────────────────────────

def test_handle_raises_orchestrator_error_on_llm_failure():
    runtime = MagicMock(spec=LLMRuntime)
    runtime.run.side_effect = LLMRuntimeError("LLM crashed")
    prompt_builder = MagicMock(spec=PromptBuilder)
    prompt_builder.build.return_value = "prompt"
    parser = MagicMock(spec=IntentParser)
    dispatcher = MagicMock(spec=ToolDispatcher)

    orc = Orchestrator(runtime, prompt_builder, dispatcher, parser)
    with pytest.raises(OrchestratorError, match="LLM runtime failed"):
        orc.handle("test")


def test_handle_raises_orchestrator_error_on_parse_error():
    runtime = MagicMock(spec=LLMRuntime)
    runtime.run.return_value = LLMResult(text="TOOL_CALL: bad", elapsed_ms=5)
    prompt_builder = MagicMock(spec=PromptBuilder)
    prompt_builder.build.return_value = "prompt"
    parser = MagicMock(spec=IntentParser)
    parser.parse.side_effect = ParseError("bad json")
    dispatcher = MagicMock(spec=ToolDispatcher)

    orc = Orchestrator(runtime, prompt_builder, dispatcher, parser)
    with pytest.raises(OrchestratorError, match="Failed to parse"):
        orc.handle("test")


def test_handle_raises_orchestrator_error_on_dispatch_failure():
    tool_call = ToolCall(tool="finance.add_expense", args={})
    runtime = MagicMock(spec=LLMRuntime)
    runtime.run.return_value = LLMResult(text="TOOL_CALL: ...", elapsed_ms=5)
    prompt_builder = MagicMock(spec=PromptBuilder)
    prompt_builder.build.return_value = "prompt"
    parser = MagicMock(spec=IntentParser)
    parser.parse.return_value = tool_call
    dispatcher = MagicMock(spec=ToolDispatcher)
    dispatcher.dispatch.side_effect = DispatchError("tool failed")

    orc = Orchestrator(runtime, prompt_builder, dispatcher, parser)
    with pytest.raises(OrchestratorError, match="Tool dispatch failed"):
        orc.handle("test")
