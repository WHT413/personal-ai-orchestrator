"""Unit tests for Orchestrator (Phase 1 Hybrid Pipeline)."""

import json
import pytest
from unittest.mock import MagicMock

from interfaces.llm_runtime import LLMRuntime, LLMResult, LLMRuntimeError
from routing.intent_router import HybridIntentRouter, RouteResult
from core.orchestrator import Orchestrator, OrchestratorError
from tools.tool_dispatcher import ToolDispatcher, DispatchError


def make_orchestrator(
    route_intent: str,
    route_params: dict,
    tool_result: dict | None = None,
    llm_fallback_text: str = "Fallback text",
    llm_fails: bool = False,
    dispatch_fails: bool = False,
    routing_fails: bool = False
):
    """Helper to build a fully mocked Orchestrator for Phase 1."""
    
    # Mock Router
    router = MagicMock(spec=HybridIntentRouter)
    if routing_fails:
        router.route.side_effect = RuntimeError("Router crash")
    else:
        router.route.return_value = RouteResult(intent=route_intent, params=route_params)
        
    # Mock Dispatcher
    dispatcher = MagicMock(spec=ToolDispatcher)
    if dispatch_fails:
        dispatcher.dispatch.side_effect = DispatchError("tool failed")
    elif tool_result is not None:
        dispatcher.dispatch.return_value = tool_result

    # Mock LLM Runtime
    runtime = MagicMock(spec=LLMRuntime)
    if llm_fails:
        runtime.run.side_effect = LLMRuntimeError("LLM crashed")
    else:
        runtime.run.return_value = LLMResult(text=llm_fallback_text, elapsed_ms=10)

    return Orchestrator(
        router=router,
        dispatcher=dispatcher,
        runtime=runtime,
    )


# ── conversational path ────────────────────────────────────────────────────────

def test_handle_returns_llm_text_when_conversation_intent():
    orc = make_orchestrator(
        route_intent="conversation",
        route_params={"user_input": "hi"},
        llm_fallback_text="Hello! How can I help?"
    )
    result = orc.handle("hi")
    
    assert result == "Hello! How can I help?"
    orc._dispatcher.dispatch.assert_not_called()
    orc._runtime.run.assert_called_once()
    
    # Ensure raw user input is in the prompt
    prompt = orc._runtime.run.call_args[0][0]
    assert "User: hi" in prompt


# ── tool dispatch path ─────────────────────────────────────────────────────────

def test_handle_dispatches_tool_when_intent_resolved():
    tool_result = {"id": "abc", "amount": 50000, "category": "food"}
    orc = make_orchestrator(
        route_intent="finance.add_expense",
        route_params={"user_input": "ghi 50k com"},
        tool_result=tool_result
    )

    result = orc.handle("ghi 50k com")

    orc._dispatcher.dispatch.assert_called_once_with(
        "finance.add_expense", {"user_input": "ghi 50k com"}
    )
    orc._runtime.run.assert_not_called()
    
    # Result should be JSON-formatted tool result
    parsed = json.loads(result)
    assert parsed == tool_result


# ── error paths ────────────────────────────────────────────────────────────────

def test_handle_raises_orchestrator_error_on_routing_failure():
    orc = make_orchestrator(route_intent="", route_params={}, routing_fails=True)
    with pytest.raises(OrchestratorError, match="Routing failed"):
        orc.handle("test")


def test_handle_raises_orchestrator_error_on_dispatch_failure():
    orc = make_orchestrator(
        route_intent="finance.add_expense",
        route_params={},
        dispatch_fails=True
    )
    with pytest.raises(OrchestratorError, match="Tool dispatch failed"):
        orc.handle("test")


def test_handle_raises_orchestrator_error_on_llm_fallback_failure():
    orc = make_orchestrator(
        route_intent="conversation",
        route_params={},
        llm_fails=True
    )
    with pytest.raises(OrchestratorError, match="fallback failed"):
        orc.handle("test")
