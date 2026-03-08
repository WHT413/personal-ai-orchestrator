"""Unit tests for ToolDispatcher (Phase 1)."""

import pytest
from core.tool_registry import ToolRegistry
from tools.tool_dispatcher import ToolDispatcher, DispatchError


def make_dispatcher(*registrations):
    """Helper: create a ToolDispatcher with pre-registered tools."""
    registry = ToolRegistry()
    for name, fn in registrations:
        registry.register(name, fn)
    return ToolDispatcher(registry)


def test_dispatch_calls_tool_and_returns_result():
    def my_tool(**kwargs):
        return {"status": "ok", "echo": kwargs}

    dispatcher = make_dispatcher(("test.tool", my_tool))
    result = dispatcher.dispatch("test.tool", {"x": 1})
    assert result == {"status": "ok", "echo": {"x": 1}}


def test_dispatch_unknown_tool_raises():
    dispatcher = make_dispatcher()
    with pytest.raises(DispatchError, match="finance.add_expense"):
        dispatcher.dispatch("finance.add_expense", {})


def test_dispatch_tool_exception_raises_dispatch_error():
    def failing_tool(**kwargs):
        raise RuntimeError("something went wrong")

    dispatcher = make_dispatcher(("broken.tool", failing_tool))
    with pytest.raises(DispatchError, match="something went wrong"):
        dispatcher.dispatch("broken.tool", {})


def test_dispatch_tool_returning_non_dict_raises():
    def bad_tool(**kwargs):
        return "not a dict"

    dispatcher = make_dispatcher(("bad.tool", bad_tool))
    with pytest.raises(DispatchError, match="must return a dict"):
        dispatcher.dispatch("bad.tool", {})


def test_dispatch_passes_args_correctly():
    received = {}

    def capturing_tool(**kwargs):
        received.update(kwargs)
        return {"captured": True}

    dispatcher = make_dispatcher(("capture.tool", capturing_tool))
    dispatcher.dispatch("capture.tool", {"amount": 100, "category": "food"})
    assert received == {"amount": 100, "category": "food"}
