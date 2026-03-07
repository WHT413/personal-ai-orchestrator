"""Unit tests for ToolRegistry."""

import pytest
from core.tool_registry import ToolRegistry, ToolNotFoundError


def dummy_tool(**kwargs) -> dict:
    return {"ok": True}


def test_register_and_get_tool():
    registry = ToolRegistry()
    registry.register("finance.add_expense", dummy_tool)
    fn = registry.get("finance.add_expense")
    assert fn is dummy_tool


def test_get_unknown_tool_raises():
    registry = ToolRegistry()
    with pytest.raises(ToolNotFoundError, match="finance.add_expense"):
        registry.get("finance.add_expense")


def test_duplicate_registration_raises():
    registry = ToolRegistry()
    registry.register("finance.add_expense", dummy_tool)
    with pytest.raises(ValueError, match="already registered"):
        registry.register("finance.add_expense", dummy_tool)


def test_empty_name_raises():
    registry = ToolRegistry()
    with pytest.raises(ValueError):
        registry.register("", dummy_tool)


def test_list_tools_returns_sorted():
    registry = ToolRegistry()
    registry.register("finance.query_expenses", dummy_tool)
    registry.register("finance.add_expense", dummy_tool)
    assert registry.list_tools() == ["finance.add_expense", "finance.query_expenses"]


def test_list_tools_empty_registry():
    registry = ToolRegistry()
    assert registry.list_tools() == []
